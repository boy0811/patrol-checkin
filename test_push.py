from line_push import push_today_schedule
from app import app  # ✅ 匯入你的 Flask app（前提是你有 app = Flask(__name__)）

with app.app_context():
    push_today_schedule()
