from flask import Blueprint, render_template, request, session, redirect, jsonify, flash
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

    return render_template('member_checkin_home.html', member=member, points=points)


# ✅ 掃碼頁（開啟照相機）
@checkin_bp.route('/checkin/scan/<int:point_id>')
def scan_qr(point_id):
    point = Point.query.get(point_id)
    if not point:
        return render_template('not_found.html', code=point_id)
    return render_template('scan_qr.html', point=point)


# ✅ 接收 QR 內容進行簽到（不限制 10 分鐘）
@checkin_bp.route('/checkin', methods=['POST'])
def checkin_post():
    data = request.get_json()
    point_code = data.get('point')  # ✅ QR code 傳入的地點代碼
    member_id = session.get('user_id')

    if not point_code or not member_id:
        return jsonify({"message": "❌ 資料不完整"}), 400

    point = Point.query.filter_by(code=point_code).first()
    if not point:
        return jsonify({"message": "❌ 找不到簽到點"}), 400

    # ✅ 不做重複簽到判斷，直接寫入
    record = Record(member_id=member_id, point_id=point.id, timestamp=datetime.utcnow())
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


# ✅ GET 頁面導回主頁
@checkin_bp.route('/checkin', methods=['GET'])
def checkin_redirect():
    return redirect('/member_checkin_home')


# ✅ 若你還有用 JS 拉 checked_ids，可以回傳全部紀錄
@checkin_bp.route('/checkin/status')
def checkin_status():
    member_id = session.get('user_id')
    if not member_id:
        return jsonify({'checked_ids': []})

    # 回傳所有簽到紀錄（不限制時間）
    checked_ids = [
        r.point_id for r in Record.query
        .filter_by(member_id=member_id)
        .all()
    ]
    return jsonify({'checked_ids': checked_ids})
