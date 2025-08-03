# app.py
from flask import Flask, redirect, url_for, session, render_template, send_from_directory
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

app = Flask(__name__)
app.secret_key = 'checkin_secret_key'

# ✅ 判斷 Render 環境並套用資料庫連線字串
if os.environ.get("RENDER") == "true":
    app.config['SERVER_NAME'] = 'patrol-checkin-1.onrender.com'
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

# 預設首頁導向登入
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

# 顯示目前資料庫資訊
from flask import jsonify

@app.route("/dbinfo")
def db_info():
    db_url = str(db.engine.url)
    return jsonify({
        "目前使用的資料庫": db_url
    })

# 主程式啟動
if __name__ == '__main__':
    print("✔ 使用的資料庫：", app.config['SQLALCHEMY_DATABASE_URI'])
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
