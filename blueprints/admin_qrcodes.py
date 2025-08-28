import os
import qrcode
from flask import Blueprint, render_template, session, redirect, url_for, flash
from models import db, Member, Point

admin_qrcodes_bp = Blueprint('admin_qrcodes', __name__, url_prefix='/admin/qrcodes')

QRCODE_DIR = 'static/qrcodes'
os.makedirs(QRCODE_DIR, exist_ok=True)

# ✅ 手動指定區網 IP（讓手機模擬器能掃描成功）
BASE_URL = "http://192.168.0.116:5000"  # ← 換成你自己的電腦 IP

# ✅ 權限判斷
def is_admin_user():
    if session.get('admin'):
        return True
    if 'user_id' in session:
        user = db.session.get(Member, session['user_id'])
        return user and user.title in ['隊長', '副分隊長', '分隊長']
    return False

# ✅ 主頁：列出 QR Code
@admin_qrcodes_bp.route('/')
def qrcode_list():
    if not is_admin_user():
        return redirect(url_for('login'))

    qrcodes = []
    points = Point.query.all()
    for point in points:
        filename = f"{point.code}.png"
        filepath = os.path.join(QRCODE_DIR, filename)
        if not os.path.exists(filepath):
            qr_url = f"{BASE_URL}/checkin/{point.code}"  # ✅ 手動組網址
            img = qrcode.make(qr_url)
            img.save(filepath)
        qrcodes.append({
            'code': point.code,
            'name': point.name,
            'filename': filename
        })
    return render_template('admin_qrcodes.html', qrcodes=qrcodes)

# ✅ 一鍵清除並重建
@admin_qrcodes_bp.route('/refresh', endpoint='refresh_qrcodes')
def refresh_qrcodes():
    if not is_admin_user():
        return redirect(url_for('login'))

    # 刪除舊的 QR Code 圖片
    for fname in os.listdir(QRCODE_DIR):
        if fname.endswith('.png'):
            os.remove(os.path.join(QRCODE_DIR, fname))

    # 重新產生新的
    points = Point.query.all()
    for point in points:
        filename = f"{point.code}.png"
        filepath = os.path.join(QRCODE_DIR, filename)
        qr_url = f"{BASE_URL}/checkin/{point.code}"  # ✅ 手動組網址
        img = qrcode.make(qr_url)
        img.save(filepath)

    flash("✅ 所有 QR Code 已重新建立（已清除舊檔）", "success")
    return redirect(url_for('admin_qrcodes.qrcode_list'))
