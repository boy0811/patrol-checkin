from flask import Blueprint, render_template, request, make_response, session, redirect
from models import db, Member, Point, Record
from io import StringIO
from datetime import datetime
import csv

admin_export_bp = Blueprint('admin_export', __name__, url_prefix='/admin')


# ✅ 權限判斷
def is_admin_user():
    if session.get('admin'):
        return True
    if 'user_id' in session:
        user = db.session.get(Member, session['user_id'])
        return user and user.title in ['隊長', '副分隊長', '分隊長']
    return False


# ✅ 匯出表單頁
@admin_export_bp.route('/export_form')
def export_form():
    if not is_admin_user():
        return redirect('/login')
    return render_template('admin_export_form.html')


# ✅ 處理匯出資料（CSV）
@admin_export_bp.route('/export_records', methods=['POST'])
def export_records():
    if not is_admin_user():
        return "權限不足", 403

    try:
        start = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
        end = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")
    except Exception:
        return "日期格式錯誤", 400

    records = db.session.query(
        Member.account, Member.name, Member.title,
        Record.timestamp, Point.name
    ).join(Record, Record.member_id == Member.id) \
     .join(Point, Record.point_id == Point.id) \
     .filter(Record.timestamp >= start) \
     .filter(Record.timestamp <= end) \
     .order_by(Record.timestamp).all()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["帳號", "姓名", "職稱", "簽到時間", "簽到地點"])
    for r in records:
        writer.writerow([r[0], r[1], r[2], r[3].strftime("%Y-%m-%d %H:%M:%S"), r[4]])

    output = make_response('﻿' + si.getvalue())  # 加上 BOM 避免 Excel 亂碼
    output.headers["Content-Disposition"] = "attachment; filename=簽到紀錄.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    return output
