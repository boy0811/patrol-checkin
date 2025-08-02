from flask import Blueprint, render_template, redirect, session, send_file
from models import db, Member, Point
import qrcode
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

QR_DIR = "static/qrcodes"
os.makedirs(QR_DIR, exist_ok=True)

# ✅ 判斷是否為管理員身份
def is_admin_user():
    if session.get('admin'):
        return True
    if 'user_id' in session:
        user = db.session.get(Member, session['user_id'])
        return user and user.title in ['隊長', '副分隊長', '分隊長']
    return False

# ✅ 管理員首頁
@admin_bp.route('/')
def admin_home():
    if not is_admin_user():
        return redirect('/login')
    return render_template('admin.html')

# ✅ 產生並顯示 QR Code 圖片頁
@admin_bp.route('/qrcodes')
def generate_qrcodes():
    if not is_admin_user():
        return redirect('/login')

    points = Point.query.all()
    qrcodes = []

    for point in points:
        qr_data = point.name  # 若要改成網址可改成 f"http://127.0.0.1:5000/checkin/scan/{point.id}"
        qr_path = os.path.join(QR_DIR, f"{point.name}.png")

        if not os.path.exists(qr_path):
            img = qrcode.make(qr_data)
            img.save(qr_path)

        qrcodes.append({
            "name": point.name,
            "path": f"/{qr_path}"
        })

    return render_template("admin_qrcodes.html", qrcodes=qrcodes)
