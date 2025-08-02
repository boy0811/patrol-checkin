import os
import qrcode
from flask import Blueprint, render_template, session, redirect
from models import db, Member, Point

admin_qrcodes_bp = Blueprint('admin_qrcodes', __name__, url_prefix='/admin/qrcodes')

QRCODE_DIR = 'static/qrcodes'
os.makedirs(QRCODE_DIR, exist_ok=True)

# ✅ 權限判斷
def is_admin_user():
    if session.get('admin'):
        return True
    if 'user_id' in session:
        user = db.session.get(Member, session['user_id'])
        return user and user.title in ['隊長', '副分隊長', '分隊長']
    return False

# ✅ 若主程式有這函式，就引用，否則放這裡一份
def get_ngrok_url():
    try:
        import requests
        res = requests.get("http://127.0.0.1:4040/api/tunnels")
        data = res.json()
        for t in data['tunnels']:
            if t['public_url'].startswith('http://'):
                return t['public_url']
    except:
        return "http://localhost:5000"

# ✅ QR code 生成功能
@admin_qrcodes_bp.route('/')
def admin_qrcodes():
    if not is_admin_user():
        return redirect('/login')

    base_url = get_ngrok_url() + "/checkin"
    points = Point.query.all()
    for p in points:
        url = f"{base_url}?point={p.code}"
        img = qrcode.make(url)
        img.save(os.path.join(QRCODE_DIR, f"{p.code}.png"))

    return render_template('qrcodes.html', points=points)
