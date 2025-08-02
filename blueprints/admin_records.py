from flask import Blueprint, request, send_file, render_template, redirect, session, flash, jsonify
from io import StringIO, BytesIO
from datetime import datetime
import csv

from models import db, Record, Member, Point, Report

admin_records_bp = Blueprint('admin_records', __name__, url_prefix='/admin')

# ✅ 匯出表單頁面
@admin_records_bp.route('/export_form')
def export_form():
    if not session.get('admin'):
        return redirect('/login')
    return render_template('admin/export_form.html')

# ✅ 匯出 CSV 功能
@admin_records_bp.route('/export_records', methods=['POST'])
def export_records():
    if not session.get('admin'):
        return redirect('/login')

    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        end_date = datetime.combine(end_date, datetime.max.time())
    except ValueError:
        flash("⚠️ 日期格式錯誤", "danger")
        return redirect('/admin/export_form')

    records = Record.query.filter(
        Record.timestamp >= start_date,
        Record.timestamp <= end_date
    ).all()

    str_io = StringIO()
    writer = csv.writer(str_io)
    writer.writerow(['隊員姓名', '級職', '巡邏點', '簽到時間'])
    for r in records:
        writer.writerow([
            r.member.name,
            r.member.title,
            r.point.name,
            r.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        ])

    byte_io = BytesIO()
    byte_io.write(str_io.getvalue().encode('utf-8-sig'))  # for Excel
    byte_io.seek(0)

    return send_file(
        byte_io,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'records_{start_date_str}_to_{end_date_str}.csv'
    )

# ✅ 簽到紀錄頁面
@admin_records_bp.route('/records')
def view_records():
    if not session.get('admin'):
        return redirect('/login')
    return render_template('admin/records.html')

# ✅ 提供 JS API 用於載入簽到紀錄
@admin_records_bp.route('/api/records')
def api_records():
    if not session.get('admin'):
        return jsonify([])

    records = Record.query.order_by(Record.timestamp.desc()).all()
    result = []
    for r in records:
        result.append({
            'account': r.member.account,
            'name': r.member.name,
            'point': r.point.name,
            'timestamp': r.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result)

# ✅ 顯示緊急通報紀錄頁面
@admin_records_bp.route('/reports')
def view_reports():
    if not session.get('admin'):
        return redirect('/login')

    reports = db.session.query(
        Member.account,             # ✅ 修正為 account
        Member.name,
        Report.description,
        Report.photo_filename,
        Report.timestamp
    ).join(Member, Report.member_id == Member.id).order_by(Report.timestamp.desc()).all()

    return render_template('admin/reports.html', reports=reports)
