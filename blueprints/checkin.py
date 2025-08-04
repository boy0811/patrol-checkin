from flask import Blueprint, render_template, request, session, redirect, jsonify, flash
from models import db, Member, Point, Record
from datetime import datetime
from datetime import datetime, timedelta
from pytz import timezone  # 加在檔案最上方

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


# ✅ 檢查是否在 5 分鐘內簽到過該地點
@checkin_bp.route('/checkin', methods=['POST'])
def checkin_post():
    data = request.get_json()
    point_code = data.get('point')
    expected_point_id = data.get('expected_point_id')  # 從前端送過來

    member_id = session.get('user_id')

    if not point_code or not member_id:
        return jsonify({"message": "❌ 資料不完整"}), 400

    point = Point.query.filter_by(code=point_code).first()
    if not point:
        return jsonify({"message": "❌ 找不到簽到點"}), 400

    # ✅ 地點不符阻擋
    if expected_point_id and int(expected_point_id) != point.id:
        return jsonify({
            "message": "❌ 地點不符，請掃描正確 QR Code",
            "redirect": "/member_checkin_home"
        })

    # ✅ 時間判斷（使用台灣時間）
    from pytz import timezone
    taipei = timezone('Asia/Taipei')
    now = datetime.now(taipei)
    five_minutes_ago = now - timedelta(minutes=5)

    recent_record = Record.query.filter_by(member_id=member_id, point_id=point.id)\
        .filter(Record.timestamp >= five_minutes_ago).first()

    if recent_record:
        return jsonify({
            "message": f"✅ 您已簽到成功 {point.name}",
            "redirect": "/member_checkin_home"
        })

    record = Record(member_id=member_id, point_id=point.id, timestamp=now)
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
