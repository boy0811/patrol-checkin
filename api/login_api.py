from flask import Blueprint, request, jsonify
from models import db, Member  # 根據你實際的模型修改
from werkzeug.security import check_password_hash

login_api = Blueprint('login_api', __name__)

@login_api.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    account = data.get('account')
    password = data.get('password')

    member = Member.query.filter_by(account=account).first()
    if not member or not check_password_hash(member.password_hash, password):
        return jsonify({"message": "帳號或密碼錯誤", "status": "fail"})

    return jsonify({"message": "登入成功", "status": "success", "member_id": member.id})
