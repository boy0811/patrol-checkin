from flask import Blueprint, render_template, request, session, redirect, jsonify
from models import db, Member, Point, Record
from datetime import datetime

checkin_bp = Blueprint('checkin', __name__)

# ✅ 簽到首頁：顯示所有點與已簽到點
@checkin_bp.route('/member_checkin_home')
def member_checkin_home():
    member_id = session.get('user_id')
    if not member_id:
        return redirect('/login')

    member = db.session.get(Member, member_id)
    points = Point.query.order_by(Point.id.asc()).all()
    checked_ids = [r.point_id for r in Record.query.filter_by(member_id=member_id).all()]

    return render_template('member_checkin_home.html', member=member, points=points, checked_ids=checked_ids)

# ✅ 掃碼簽到 POST API（由 JS 呼叫）
@checkin_bp.route('/checkin', methods=['POST'])
def checkin_post():
    data = request.get_json()
    point_name = data.get('point')
    member_id = session.get('user_id')

    if not point_name or not member_id:
        return jsonify({"message": "❌ 資料不完整"}), 400

    point = Point.query.filter_by(name=point_name).first()
    if not point:
        return jsonify({"message": "❌ 找不到簽到點"}), 400

    # 檢查是否已簽到過該點
    exists = Record.query.filter_by(member_id=member_id, point_id=point.id).first()
    if exists:
        return jsonify({"message": f"✅ 您已簽到過 {point.name}"}), 200

    record = Record(member_id=member_id, point_id=point.id, timestamp=datetime.now())
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "message": f"✅ {point.name} 簽到成功",
        "redirect": "/member_checkin_home"
    })

@checkin_bp.route('/checkin/scan/<int:point_id>')
def scan_qr(point_id):
    return render_template('scan_qr.html', point_id=point_id)
