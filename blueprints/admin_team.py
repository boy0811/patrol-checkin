from flask import Blueprint, render_template, request, redirect, flash, session, url_for
from models import db, Team
import os

admin_team_bp = Blueprint('admin_team', __name__, url_prefix='/admin')

def _need_admin():
    return session.get('admin') is True

@admin_team_bp.route('/team', methods=['GET', 'POST'])
def admin_team():
    # 權限檢查
    if not _need_admin():
        flash("❌ 沒有權限", "danger")
        return redirect(url_for("auth.login"))

    team = Team.query.first()

    # ✅ 如果還沒有隊伍資料，就建立一筆
    if not team:
        team = Team(name='', station_name='', phone_number='')
        db.session.add(team)
        db.session.commit()
        print("🆕 新建一筆空白 Team:", team.__dict__)

    if request.method == 'POST':
        try:
            # 使用 (.. or '').strip() 確保 None 變成空字串
            team.name = (request.form.get('name') or '').strip()
            team.station_name = (request.form.get('station_name') or '').strip()
            team.phone_number = (request.form.get('phone_number') or '').strip()

            print("📌 更新前:", team.__dict__)   # 🟡 Debug：更新前資料

            db.session.commit()
            db.session.refresh(team)   # 確保馬上刷新

            print("✅ 更新後:", team.__dict__)   # 🟢 Debug：更新後資料

            flash(f'✅ 資料已更新：{team.station_name}, {team.phone_number}', 'success')

        except Exception as e:
            db.session.rollback()
            print("❌ 更新失敗，錯誤:", e)
            flash(f'❌ 儲存失敗：{e}', 'danger')

        return redirect(url_for('admin_team.admin_team'))   # 回到同一頁

    return render_template('admin_team_form.html', team=team)
