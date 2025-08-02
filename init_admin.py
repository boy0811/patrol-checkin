# init_admin.py
from app import app, db
from models import Member
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        account = 'admin'
        password = '1234'
        name = '管理員'
        title = '隊長'

        # 檢查是否已有此帳號
        existing = Member.query.filter_by(account=account).first()
        if existing:
            print(f'❗帳號 "{account}" 已存在，略過建立。')
            return

        # 建立新帳號
        hashed_pw = generate_password_hash(password)
        admin = Member(account=account, password_hash=hashed_pw, name=name, title=title)
        db.session.add(admin)
        db.session.commit()
        print(f'✅ 已建立帳號 "{account}"，預設密碼為 "{password}"')

if __name__ == '__main__':
    create_admin()
