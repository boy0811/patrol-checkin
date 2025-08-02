from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Member
from werkzeug.security import generate_password_hash

admin_members_bp = Blueprint('admin_members', __name__, url_prefix='/admin/members')

# 權限檢查：只有管理員可用
def is_admin_user():
    if session.get('admin'):
        return True
    if 'user_id' in session:
        user = db.session.get(Member, session['user_id'])
        return user and user.title in ['隊長', '副分隊長', '分隊長']
    return False

@admin_members_bp.route('/', methods=['GET', 'POST'])
def admin_members():
    if not is_admin_user():
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        name = request.form['name']
        account = request.form['account']
        password = request.form['password']

        if Member.query.filter_by(account=account).first():
            flash('⚠️ 帳號已存在，請重新輸入', 'warning')
        else:
            new_member = Member(
                title=title,
                name=name,
                account=account,
                password_hash=generate_password_hash(password)
            )
            db.session.add(new_member)
            db.session.commit()
            flash('✅ 已新增隊員', 'success')

    members = Member.query.order_by(Member.id).all()
    return render_template('admin_members.html', members=members)

@admin_members_bp.route('/delete/<int:member_id>')
def delete_member(member_id):
    if not is_admin_user():
        return redirect('/login')
    member = db.session.get(Member, member_id)
    if member:
        db.session.delete(member)
        db.session.commit()
        flash('✅ 已刪除', 'success')
    else:
        flash('⚠️ 找不到該隊員', 'danger')
    return redirect(url_for('admin_members.admin_members'))

@admin_members_bp.route('/edit/<int:member_id>', methods=['GET', 'POST'])  # ✅ 修正路徑
def edit_member(member_id):
    if not is_admin_user():
        return redirect('/login')

    member = db.session.get(Member, member_id)
    if not member:
        flash("找不到該隊員", "danger")
        return redirect(url_for('admin_members.admin_members'))

    if request.method == 'POST':
        member.title = request.form['title']
        member.name = request.form['name']
        # account 不允許修改
        password = request.form['password']
        if password:
            member.password_hash = generate_password_hash(password)

        db.session.commit()
        flash("✅ 修改成功", "success")
        return redirect(url_for('admin_members.admin_members'))

    return render_template('admin_member_edit.html', member=member)
