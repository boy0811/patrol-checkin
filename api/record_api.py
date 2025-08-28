from flask import Blueprint, request, jsonify
from models import db, Record

record_api = Blueprint('record_api', __name__)

@record_api.route('/api/records', methods=['GET'])
def get_records():
    records = Record.query.order_by(Record.timestamp.desc()).all()
    result = []

    for record in records:
        result.append({
            'id': record.id,
            'member_id': record.member_id,
            'point_id': record.point_id,
            'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({'status': 'success', 'records': result})
