# checkin_system/api/team.py

import os
import time
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from models import db, Team

team_api = Blueprint('team_api', __name__, url_prefix='/api/team')

# ---- 既有：建立/更新隊伍資訊 ----
@team_api.route('/setup', methods=['POST'])
def setup_team():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    station_name = data.get('station_name')

    team = Team.query.first()
    if team:
        team.name = name
        team.phone_number = phone
        team.station_name = station_name
    else:
        team = Team(name=name, phone_number=phone, station_name=station_name)
        db.session.add(team)

    db.session.commit()
    return jsonify({'message': '✅ 設定成功'})

# ---- 既有：取得隊伍資訊 ----
@team_api.route('/info')
def team_info():
    team = Team.query.first()
    if team:
        return jsonify({
            'name': team.name,
            'station_name': team.station_name,
            'phone': team.phone_number
        })
    else:
        return jsonify({'error': 'No team found'}), 404


# ===============================
#        🔽 新增：LOGO API
# ===============================

ALLOWED_EXTS = {'.png', '.jpg', '.jpeg', '.webp'}
LOGO_DIR = os.path.join('static', 'logo')
LOGO_PATH = os.path.join(LOGO_DIR, 'logo.png')  # 統一存成 logo.png

def _ensure_logo_dir():
    os.makedirs(LOGO_DIR, exist_ok=True)

# 上傳/更換 LOGO（表單欄位名稱：logo）
@team_api.route('/upload_logo', methods=['POST'])
def upload_logo():
    _ensure_logo_dir()

    file = request.files.get('logo')
    if not file or not file.filename:
        return jsonify({'error': 'No file'}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTS:
        return jsonify({'error': 'Only png/jpg/jpeg/webp allowed'}), 400

    # 可先 secure 一下檔名（雖然我們固定存成 logo.png）
    _ = secure_filename(file.filename)

    # 統一覆蓋為 logo.png（前端比較單純）
    file.save(LOGO_PATH)

    ts = int(time.time())
    return jsonify({'message': 'ok', 'url': f'/static/logo/logo.png?v={ts}'})

# 取得目前 LOGO 的 URL（無則回傳 exists=False）
@team_api.route('/logo_url', methods=['GET'])
def logo_url():
    if os.path.exists(LOGO_PATH):
        ts = int(os.path.getmtime(LOGO_PATH))
        return jsonify({'exists': True, 'url': f'/static/logo/logo.png?v={ts}'})
    return jsonify({'exists': False, 'url': None})
