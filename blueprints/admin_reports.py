from flask import Blueprint, render_template, session, redirect
from models import db, Member, Report

admin_reports_bp = Blueprint('admin_reports', __name__, url_prefix='/admin/reports')


# ✅ 權限判斷（可與其他共用）
def is_admin_user():
    if session.get('admin'):
        return True
    if 'user_id' in session:
        user = db.session.get(Member, session['user_id'])
        return user and user.title in ['隊長', '副分隊長', '分隊長']
    return False


# ✅ 顯示回報紀錄
@admin_reports_bp.route('/')
def view_reports():
    if not is_admin_user():
        return redirect('/login')
    reports = Report.query.all()
    data = [{
        'name': r.member.name,
        'desc': r.description,
        'photo': r.photo_filename,
        'time': r.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for r in reports]
    return render_template('reports.html', reports=data)
