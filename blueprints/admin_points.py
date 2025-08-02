# blueprints/admin_points.py

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Point

admin_points_bp = Blueprint('admin_points', __name__, url_prefix='/admin/points')

def is_admin_user():
    return session.get('admin')

# 🔹 巡邏點列表與新增
@admin_points_bp.route('/', methods=['GET', 'POST'])
def manage_points():
    if not is_admin_user():
        return redirect('/login')

    if request.method == 'POST':
        code = request.form['code']
        name = request.form['name']
        if Point.query.filter_by(code=code).first():
            flash('⚠️ 巡邏點代碼已存在', 'warning')
        else:
            new_point = Point(code=code, name=name)
            db.session.add(new_point)
            db.session.commit()
            flash('✅ 已新增巡邏點', 'success')

    points = Point.query.order_by(Point.id).all()
    return render_template('admin_points.html', points=points)

# 🔸 刪除巡邏點
@admin_points_bp.route('/delete/<int:point_id>')
def delete_point(point_id):
    if not is_admin_user():
        return redirect('/login')

    point = Point.query.get(point_id)
    if point:
        db.session.delete(point)
        db.session.commit()
        flash('✅ 已刪除巡邏點', 'success')
    else:
        flash('⚠️ 找不到該巡邏點', 'danger')
    return redirect(url_for('admin_points.manage_points'))

# 🔸 編輯巡邏點（僅支援名稱修改）
@admin_points_bp.route('/edit/<int:point_id>', methods=['GET', 'POST'])
def edit_point(point_id):
    if not is_admin_user():
        return redirect('/login')

    point = Point.query.get(point_id)
    if not point:
        flash('⚠️ 找不到該巡邏點', 'danger')
        return redirect(url_for('admin_points.manage_points'))

    if request.method == 'POST':
        point.name = request.form['name']
        db.session.commit()
        flash('✅ 已更新巡邏點', 'success')
        return redirect(url_for('admin_points.manage_points'))

    return render_template('admin_point_edit.html', point=point)
