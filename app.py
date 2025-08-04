# app.py
from flask import Flask, redirect, url_for, session, render_template, send_from_directory, jsonify
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
from models import Member, Point  # ← ⬅️ 加入 Point


import os
import click
from flask.cli import with_appcontext

app = Flask(__name__)
app.secret_key = 'checkin_secret_key'

# ✅ 判斷 Render 環境並套用資料庫連線字串
if os.environ.get("RENDER") == "true":
    # ❌ 注意：這一行會導致部分路由無法運作，應該註解掉
    # app.config['SERVER_NAME'] = 'patrol-checkin-1.onrender.com'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL") + "?sslmode=require"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///checkin.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 註冊 Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(admin_members_bp)
app.register_blueprint(admin_points_bp)
app.register_blueprint(admin_records_bp)
app.register_blueprint(checkin_bp)
app.register_blueprint(admin_qrcodes_bp)
app.register_blueprint(emergency_bp)

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
        admin.set_password('1234')  # ✅ 用 set_password 儲存雜湊
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
    admin.set_password('1234')  # ✅ 正確建立密碼雜湊
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

    # 新增管理員帳號
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

# force git detect change
# ✅ 主程式（僅限本地測試）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ⬅️ 使用 Render 指定的 PORT，預設為 5000
    app.run(host='0.0.0.0', port=port)