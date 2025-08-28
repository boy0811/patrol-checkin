from flask import Blueprint, render_template, request, redirect, flash, session, url_for
from models import db, Member, Schedule
from io import TextIOWrapper
from datetime import datetime, date
from .auth import is_admin_user  # 請確認你有這個檔案與方法
from flask import jsonify
from sqlalchemy.orm import joinedload
from datetime import datetime
import csv

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')


# 🔹 提供給 App 的 API：/schedule/api?from=YYYY-MM-DD&to=YYYY-MM-DD&member_id=123 (參數都可省略)
@schedule_bp.route('/api', methods=['GET'])
def schedule_api():
    q = (Schedule.query
         .options(joinedload(Schedule.member))
         .order_by(Schedule.date.asc(), Schedule.member_id.asc()))

    date_from = request.args.get('from')
    date_to = request.args.get('to')
    member_id = request.args.get('member_id')

    if date_from:
        q = q.filter(Schedule.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        q = q.filter(Schedule.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
    if member_id:
        q = q.filter(Schedule.member_id == int(member_id))

    data = [{
        "id": s.id,
        "date": s.date.isoformat(),
        "member_id": s.member_id,
        "member_name": (s.member.name if s.member else ""),
        "duty_type": s.duty_type or "巡邏",
    } for s in q.all()]

    return jsonify(data)

# 🔹 班表主頁（全部班表）
@schedule_bp.route('/')
def schedule_home():
    schedules = Schedule.query.order_by(Schedule.date.asc()).all()
    return render_template('schedule_list.html', schedules=schedules)

# 🔹 匯入班表
@schedule_bp.route('/import', methods=['GET', 'POST'])
def import_schedule():
    if not is_admin_user():
        flash("❌ 您沒有權限", "danger")
        return redirect(url_for('schedule.schedule_home'))

    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash('❌ 請選擇檔案', 'danger')
            return redirect(url_for('schedule.import_schedule'))

        stream = TextIOWrapper(file.stream, encoding='utf-8')
        reader = csv.DictReader(stream)

        count = 0
        for row in reader:
            date_str = row.get('日期')
            title = row.get('職稱')
            name = row.get('姓名')
            duty_type = row.get('勤務')

            if not (date_str and title and name and duty_type):
                continue

            member = Member.query.filter_by(name=name.strip(), title=title.strip()).first()
            if not member:
                continue

            try:
                date_obj = datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
                schedule = Schedule(
                    member_id=member.id,
                    date=date_obj,
                    duty_type=duty_type.strip()
                )
                db.session.add(schedule)
                count += 1
            except Exception as e:
                print(f"⛔ 跳過錯誤列：{row}，錯誤：{e}")
                continue

        db.session.commit()
        flash(f'✅ 匯入成功，共 {count} 筆資料', 'success')
        return redirect(url_for('schedule.schedule_home'))

    return render_template('schedule_import.html')

# 🔹 新增單筆排班
@schedule_bp.route('/add', methods=['GET', 'POST'])
def add_schedule():
    if not is_admin_user():
        flash("❌ 您沒有權限", "danger")
        return redirect(url_for('schedule.schedule_home'))

    if request.method == 'POST':
        member_id = request.form.get('member_id')
        date_str = request.form.get('date')
        duty_type = request.form.get('duty_type')

        if member_id and date_str and duty_type:
            try:
                date_obj = datetime.strptime(date_str.strip(), '%Y-%m-%d').date()

                # 可選：防止同人同日重複排班
                exists = Schedule.query.filter_by(member_id=member_id, date=date_obj).first()
                if exists:
                    flash("⚠️ 此成員在該日已有排班", "warning")
                    return redirect(url_for('schedule.add_schedule'))

                new_entry = Schedule(
                    member_id=member_id,
                    date=date_obj,
                    duty_type=duty_type.strip()
                )
                db.session.add(new_entry)
                db.session.commit()
                flash("✅ 排班資料已新增", "success")
                return redirect(url_for('schedule.schedule_home'))
            except Exception as e:
                flash(f"❌ 發生錯誤：{e}", "danger")
        else:
            flash("❌ 資料不完整", "danger")

    members = Member.query.order_by(Member.name).all()
    return render_template('schedule_add.html', members=members)

# 🔹 顯示今日班表
@schedule_bp.route('/today')
def today_schedule():
    today = date.today()
    schedules = Schedule.query.filter_by(date=today).all()

    patrol_members = []
    office_members = []
    inspector_members = []

    for s in schedules:
        if not s.member:
            continue
        person = {"name": s.member.name, "title": s.member.title or ""}
        if s.duty_type == "巡邏":
            patrol_members.append(person)
        elif s.duty_type == "內勤":
            office_members.append(person)
        elif s.duty_type == "督勤":
            inspector_members.append(person)

    return render_template("schedule_today.html",
                           patrol_members=patrol_members,
                           office_members=office_members,
                           inspector_members=inspector_members)
