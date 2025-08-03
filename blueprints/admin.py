from flask import Blueprint, render_template, redirect, session, send_file
from models import db, Member, Point
from models import Report
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

@admin_bp.route('/admin/')
def admin_dashboard():
    # 查詢是否有未處理的通報（你可以自訂條件，如 timestamp 在今天 或全部）
    unread_reports = Report.query.order_by(Report.timestamp.desc()).all()
    has_reports = len(unread_reports) > 0

    return render_template('admin_dashboard.html', has_reports=has_reports)
