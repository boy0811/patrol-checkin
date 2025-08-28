from flask import Blueprint, request, jsonify
from models import db, Member, Report
from datetime import datetime

report_api = Blueprint('report_api', __name__)

@report_api.route('/api/report', methods=['POST'])
def create_report():
    data = request.get_json()
    member_id = data.get('member_id')
    description = data.get('description')
    location = data.get('location')
    photo_filename = data.get('photo_filename')

    if not all([member_id, description, location]):
        return jsonify({'status': 'fail', 'message': '缺少必要欄位'}), 400

    new_report = Report(
        member_id=member_id,
        description=description,
        location=location,
        photo_filename=photo_filename,
        timestamp=datetime.now()
    )
    db.session.add(new_report)
    db.session.commit()

    return jsonify({'status': 'success', 'message': '通報成功'})
