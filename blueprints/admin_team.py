from flask import Blueprint, render_template, request, redirect, flash
from models import db, Team
import os

admin_team_bp = Blueprint('admin_team', __name__, url_prefix='/admin')

@admin_team_bp.route('/team', methods=['GET', 'POST'])
def admin_team():
    team = Team.query.first()
    if request.method == 'POST':
        team.name = request.form.get('name') or ''
        team.station_name = request.form.get('station_name') or ''
        team.phone_number = request.form.get('phone_number') or ''
        db.session.commit()
        flash('✅ 資料已更新', 'success')
        return redirect('/admin')

    return render_template('admin_team_form.html', team=team)

@admin_team_bp.route('/upload_logo', methods=['GET', 'POST'])
def upload_logo():
    if request.method == 'POST':
        file = request.files.get('logo')
        if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filename = 'logo.png'
            save_path = os.path.join('static', 'logo')
            os.makedirs(save_path, exist_ok=True)
            file.save(os.path.join(save_path, filename))
            flash('✅ Logo 上傳成功！', 'success')
        else:
            flash('❌ 請選擇 PNG / JPG 圖片', 'danger')
        return redirect('/admin/upload_logo')

    # ✅ 判斷是否已有 logo
    logo_exists = os.path.exists(os.path.join('static', 'logo', 'logo.png'))
    return render_template('admin_logo_upload.html', logo_exists=logo_exists)
