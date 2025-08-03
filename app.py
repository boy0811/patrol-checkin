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

import os
import click
from flask.cli import with_appcontext

app = Flask(__name__)
app.secret_key = 'checkin_secret_key'

# ✅ 判斷 Render 環境並套用資料庫連線字串
if os.environ.get("RENDER") == "true":
    # ❌ 注意：這一行會導致部分路由無法運作，應該註解掉
    # app.config['SERVER_NAME'] = 'patrol-checkin-1.onrender.com'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
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

# ✅ 臨時網頁建表（部署後可透過網址觸發）
@app.route("/initdb")
def init_db_web():
    if not session.get("admin"):
        return "⛔ 你沒有權限使用此功能", 403
    try:
        db.create_all()
        return "✅ 資料表已成功建立"
    except Exception as e:
        return f"❌ 建立失敗：{e}"

from models import Member  # 確保有這一行
from werkzeug.security import generate_password_hash  # ⬅️ 加上這

@app.route('/create-admin')
def create_admin():
    existing = Member.query.filter_by(account='admin').first()
    if existing:
        return "⚠️ 管理員已存在"

    from werkzeug.security import generate_password_hash
    admin = Member(
        account='admin',
        password_hash=generate_password_hash('1234'),
        name='管理員',
        title='隊長'
    )
    db.session.add(admin)
    db.session.commit()

    # 🔥 自我刪除機制（建議部署環境才啟用）
    import os
    import re
    with open(__file__, 'r', encoding='utf-8') as f:
        code = f.read()
    new_code = re.sub(r'@app\.route\([\'"]\/create-admin[\'"]\)[\s\S]+?return "✅ 已建立預設管理員 admin \/ 1234"', '', code)
    with open(__file__, 'w', encoding='utf-8') as f:
        f.write(new_code)

    return "✅ 已建立預設管理員 admin / 1234，且此路由已自動移除"

@app.route("/admin/rebuild-db")
def rebuild_db():
    from models import db
    db.drop_all()
    db.create_all()
    return "✅ 已重建資料庫（所有資料已清空）"

# force git detect change
# ✅ 主程式（僅限本地測試）
if __name__ == '__main__':
    print("✔ 使用的資料庫：", app.config['SQLALCHEMY_DATABASE_URI'])
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
