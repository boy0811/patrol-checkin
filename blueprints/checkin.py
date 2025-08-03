from flask import Blueprint, render_template, request, session, redirect, jsonify
from models import db, Member, Point, Record
from datetime import datetime

checkin_bp = Blueprint('checkin', __name__)

# ✅ 簽到首頁（按鈕列表）
@checkin_bp.route('/member_checkin_home')
def member_checkin_home():
    member_id = session.get('user_id')
    if not member_id:
        return redirect('/login')

    member = db.session.get(Member, member_id)
    points = Point.query.order_by(Point.id.asc()).all()
    checked_ids = [r.point_id for r in Record.query.filter_by(member_id=member_id).all()]
    return render_template('member_checkin_home.html', member=member, points=points, checked_ids=checked_ids)

# ✅ 掃碼頁（開啟照相機）
@checkin_bp.route('/checkin/scan/<int:point_id>')
def scan_qr(point_id):
    point = Point.query.get(point_id)
    if not point:
        return render_template('not_found.html', code=point_id)
    return render_template('scan_qr.html', point=point)

# ✅ 接收 QR 內容進行簽到
@checkin_bp.route('/checkin', methods=['POST'])
def checkin_post():
    data = request.get_json()
    point_code = data.get('point')  # ✅ 改為 code
    member_id = session.get('user_id')

    if not point_code or not member_id:
        return jsonify({"message": "❌ 資料不完整"}), 400

    point = Point.query.filter_by(code=point_code).first()  # ✅ 用 code 查
    if not point:
        return jsonify({"message": "❌ 找不到簽到點"}), 400

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

# ✅ 處理 QR Code 開啟的網址
@checkin_bp.route('/checkin/<code>')
def checkin_by_code(code):
    point = Point.query.filter_by(code=code).first()
    if not point:
        return render_template('not_found.html', code=code)
    return render_template('scan_qr.html', point=point)

# ✅ 加這個處理 GET /checkin 頁面
@checkin_bp.route('/checkin', methods=['GET'])
def checkin_redirect():
    return redirect('/member_checkin_home')
