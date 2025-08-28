# line_push.py
from linebot import LineBotApi
from linebot.models import TextSendMessage
from datetime import date
from models import db, Schedule

LINE_CHANNEL_ACCESS_TOKEN = '你的長期 token'
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def push_today_schedule_to_individuals():
    today = date.today()
    schedules = Schedule.query.filter_by(date=today).all()

    pushed_count = 0

    for s in schedules:
        member = s.member
        if not member or not member.line_user_id:
            continue

        message = f"📅 {today.strftime('%Y/%m/%d')} 您今日排班如下：\n🔸 {member.title} {member.name}（{s.duty_type}）"
        try:
            line_bot_api.push_message(
                member.line_user_id,
                TextSendMessage(text=message)
            )
            pushed_count += 1
        except Exception as e:
            print(f"❌ 推播失敗：{member.name}，錯誤：{e}")

    print(f"✅ 個別推播完成，共 {pushed_count} 人")
