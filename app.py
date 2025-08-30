from flask import Flask, redirect, url_for, session, render_template, send_from_directory, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from models import db
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.admin_members import admin_members_bp
from blueprints.admin_points import admin_points_bp
from blueprints.admin_records import admin_records_bp
from blueprints.checkin import checkin_bp
from blueprints.admin_qrcodes import admin_qrcodes_bp
from blueprints.emergency import emergency_bp
from models import Member, Point 
from blueprints.schedule import schedule_bp
from line_push import push_today_schedule_to_individuals
from apscheduler.schedulers.background import BackgroundScheduler
from flask.cli import with_appcontext
from api.team import team_api
from blueprints.admin_team import admin_team_bp

import os
import click
import atexit

app = Flask(__name__)
app.secret_key = 'checkin_secret_key'

# ✅ 判斷 Render 環境並套用資料庫連線字串
if os.environ.get("RENDER") == "true":
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///checkin.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ✅ 自動建立資料表（避免 Render PostgreSQL 沒有初始化時出錯）
with app.app_context():
    db.create_all()

# 註冊 Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(admin_members_bp)
app.register_blueprint(admin_points_bp)
app.register_blueprint(admin_records_bp)
app.register_blueprint(checkin_bp)
app.register_blueprint(admin_qrcodes_bp)
app.register_blueprint(emergency_bp)
app.register_blueprint(schedule_bp)
app.register_blueprint(team_api)
app.register_blueprint(admin_team_bp)


# ✅ 啟動每日定時推播排班通知（早上7點）
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=push_today_schedule_to_individuals, trigger="cron", hour=7, minute=0)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

start_scheduler()

# ✅ 預設首頁導向登入
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# ✅ 上傳資料夾
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

# ✅ 顯示目前資料庫連線
@app.route("/dbinfo")
def db_info():
    db_url = str(db.engine.url)
    return jsonify({"目前使用的資料庫": db_url})

# ✅ CLI 初始化指令（for render.yaml）
@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo("✅ 資料庫初始化完成")

app.cli.add_command(init_db_command)

@app.route('/create-admin')
def create_admin():
    try:
        if Member.query.filter_by(account='admin').first():
            return '⚠️ 已經有 admin 帳號'

        admin = Member(
            account='admin',
            name='管理員',
            title='隊長'
        )
        admin.set_password('1234')  
        db.session.add(admin)
        db.session.commit()
        return '✅ 管理員 admin / 1234 已建立'
    except Exception as e:
        return f'❌ 發生錯誤：{e}'

@app.route('/rebuild-db')
def rebuild_db():
    db.drop_all()
    db.create_all()

    admin = Member(account='admin', title='隊長', name='管理員')
    admin.set_password('1234')
    db.session.add(admin)

    points = [
        Point(code='A01', name='大門口'),
        Point(code='A02', name='操場'),
        Point(code='A03', name='後門'),
    ]
    db.session.add_all(points)

    db.session.commit()
    return '✅ 資料庫已重建，並加入管理員與巡邏點！'

@app.route("/dev-init")
def dev_init():
    from models import db, Member
    db.create_all()

    if not Member.query.filter_by(account='admin').first():
        admin = Member(account='admin', name='管理員', title='隊長')
        admin.set_password('1234')
        db.session.add(admin)
        db.session.commit()

    return "✅ 初始化成功，已建立資料表與預設 admin 帳號（admin/1234）"

@app.route("/dbtest")
def db_test():
    try:
        conn = db.engine.connect()
        conn.close()
        return "✅ 成功連線到資料庫"
    except Exception as e:
        return f"❌ 無法連線到資料庫：{e}"

@app.route('/bind_line', methods=['GET', 'POST'])
def bind_line():
    if request.method == 'POST':
        acc = request.form.get('account')
        user_id = request.form.get('user_id')

        member = Member.query.filter_by(account=acc).first()
        if member:
            member.line_user_id = user_id
            db.session.commit()
            return '✅ 綁定成功'
        return '❌ 找不到帳號，請確認輸入正確'

    return render_template('bind_line.html')

@app.route('/admin/line_bind_list')
def admin_line_bind_list():
    members = Member.query.order_by(Member.title, Member.name).all()
    return render_template('admin_line_binds.html', members=members)

@app.route('/fix-team-name')
def fix_team_name():
    from models import Team
    team = Team.query.first()
    if team:
        team.name = "文化志工隊"
        db.session.commit()
        return '✅ 已補上隊伍名稱'
    return '❌ 沒有隊伍資料'

@app.context_processor
def inject_team_info():
    from models import Team
    import os
    db.session.expire_all()  # ✅ 清掉快取，下次 query 一定讀最新資料

    team = Team.query.first()
    logo_exists = os.path.exists(os.path.join("static", "logo", "logo.png"))

    return dict(team_info={
        'name': (team.name if team and team.name else '未設定隊伍'),
        'station': (team.station_name if team and team.station_name else '未設定警察局'),
        'phone': (team.phone_number if team and team.phone_number else '未設定電話'),
        'logo': logo_exists
    })


@app.route("/reset-team")
def reset_team():
    from models import Team, db
    db.drop_all()
    db.create_all()
    team = Team(name="復旦里守望相助隊", station_name="桃園分局", phone_number="03-1234567")
    db.session.add(team)
    db.session.commit()
    return "✅ Team 資料表已重建，並建立一筆測試資料"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
