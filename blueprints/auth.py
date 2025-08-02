from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Member
from werkzeug.security import check_password_hash
from models import db, Member, Point, Record

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("您已成功登出", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        acc = request.form['account']
        pwd = request.form['password']
        member = Member.query.filter_by(account=acc).first()

        if member and check_password_hash(member.password_hash, pwd):
            session['user_id'] = member.id
            session['login_role'] = 'member'

            # ✅ 設定 admin 權限：只有管理職稱才設 True
            if member.title in ['隊長', '副分隊長', '分隊長']:
                session['admin'] = True
            else:
                session.pop('admin', None)

            return redirect(url_for('auth.entry'))
        else:
            flash('帳號或密碼錯誤', 'danger')

    return render_template('login.html')

@auth_bp.route('/entry')
def entry():
    user_id = session.get('user_id')
    if not user_id:
        flash("請先登入", "warning")
        return redirect(url_for('auth.login'))

    member = db.session.get(Member, user_id)
    if not member:
        session.clear()
        flash("找不到使用者，請重新登入", "danger")
        return redirect(url_for('auth.login'))

    return render_template('entry.html', member=member)

@auth_bp.route('/member_checkin_home')
def member_checkin_home():
    member_id = session.get('user_id')
    if not member_id:
        return redirect(url_for('auth.login'))

    member = db.session.get(Member, member_id)
    points = Point.query.order_by(Point.id.asc()).all()
    checked_ids = [r.point_id for r in Record.query.filter_by(member_id=member_id).all()]

    return render_template('member_checkin_home.html', member=member, points=points, checked_ids=checked_ids)
