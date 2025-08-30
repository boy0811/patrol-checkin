from flask import Blueprint, render_template, request, redirect, flash, session, url_for
from models import db, Team

# Blueprint 註冊
admin_team_bp = Blueprint('admin_team', __name__, url_prefix='/admin')

# 權限檢查
def _need_admin():
    return session.get('admin') is True

@admin_team_bp.route('/team', methods=['GET', 'POST'])
def admin_team():
    # 權限檢查
    if not _need_admin():
        flash("❌ 沒有權限", "danger")
        return redirect(url_for("auth.login"))

    team = Team.query.first()

    # 如果還沒有隊伍資料，就自動建立一筆
    if not team:
        team = Team(name='', station_name='', phone_number='')
        db.session.add(team)
        db.session.commit()
        print("🆕 新建一筆空白 Team:", team.__dict__)

    if request.method == 'POST':
        try:
            print("🔥 進來 POST /admin/team")
            print("📩 收到表單:", dict(request.form))

            # 更新資料
            team.name = (request.form.get('name') or '').strip()
            team.station_name = (request.form.get('station_name') or '').strip()
            team.phone_number = (request.form.get('phone_number') or '').strip()

            db.session.add(team)   # 確保被追蹤
            db.session.commit()

            # 再查一次確認
            updated_team = Team.query.first()
            print("✅ 更新後:", updated_team.name, updated_team.station_name, updated_team.phone_number)

            flash(f'✅ 資料已更新：{updated_team.station_name}, {updated_team.phone_number}', 'success')

        except Exception as e:
            db.session.rollback()
            print("❌ 更新失敗:", e)
            flash(f'❌ 儲存失敗：{e}', 'danger')

        return redirect(url_for('admin_team.admin_team'))

    # GET 請求 → 顯示頁面
    return render_template('admin_team.html', team=team)
