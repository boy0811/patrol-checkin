from flask import Blueprint, request, jsonify
from models import db, Member, Point, Record
from datetime import datetime

checkin_api = Blueprint('checkin_api', __name__)

@checkin_api.route('/api/checkin', methods=['POST'])
def checkin():
    data = request.get_json()
    member_id = data.get('member_id')
    point_id = data.get('point_id')

    if not member_id or not point_id:
        return jsonify({"status": "fail", "message": "缺少必要參數"})

    new_record = Record(member_id=member_id, point_id=point_id, timestamp=datetime.now())
    db.session.add(new_record)
    db.session.commit()

    return jsonify({"status": "success", "message": "簽到成功"})
