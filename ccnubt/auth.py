# coding:utf-8
from flask import Blueprint, jsonify, request, abort
import json, requests, hashlib, datetime
from .model import User
from . import db, store
from wsgi import app
from flask_login import login_required, login_user, current_user


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        abort(403)
    resp_data = {
        "result_code": -1,
        "err_msg": ""
    }
    data = request.get_data()
    print(data)
    try:
        json_code = json.loads(data)['code']
    except:
        resp_data['err_msg'] = 'cant loads code'
        return jsonify(resp_data)
    appid = 'wxc48512bec9cdd899'
    secret = '7706006289fe3fa21f00fffa53a8e851'
    url = "https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code"
    url = url % (appid, secret, json_code)
    try:
        resp = requests.get(url, timeout=30)
        resp_json = json.loads(resp.text)
        openid = resp_json['openid']
        session_key = resp_json['session_key']
    except:
        resp_data['err_msg'] = 'code error or system error'
        return jsonify(resp_data)
    key = openid + session_key

    user = User.query.filter_by(openid=openid).first()
    api_key = hashlib.md5(key.encode('utf-8')).hexdigest()
    # print(api_key)
    store.set(api_key, openid, 60*60*24*2)

    if not user :
        user = User()
        user.openid = openid
        resp_data = {
            "result_code": 2,  # 用户未注册
            "api_key": api_key,
            "user_info": {
                "role": 0
            }
        }
    elif not user.active:
        abort(403)
    elif not user.enable:
        resp_data = {
            "result_code": 2,  # 用户未注册
            "api_key": api_key,
            "user_info": {
                "role": 0
            }
        }
    else:
        resp_data = {
            "result_code": 1,
            "api_key": api_key,
            "user_info": {
                "role": user.role,
                "name": user.name,
                "phone":user.phone,
                "qq": user.qq,
                "sex": user.sex
            }
        }
    user.api_key = api_key
    user.last_active_time = datetime.datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify(resp_data)
'''
{
  "data":{
    "info":{
      ""
    }
  }
}
'''

@bp.route('register/', methods=['POST'])
@login_required
def register():
    json_data = json.loads(request.data)
    info = json_data.get("info")
    user = current_user
    user.name = info.get("name")
    user.sex = info.get("sex")
    user.phone = info.get("phone")
    user.qq = info.get("qq")
    user.enable = True
    try:
        db.session.add(user)
        db.session.commit()
        resp = {
            "result_code": 1,
            "msg": "register sucess",
            "user_info": {
                "name": user.name,
                "role": user.role,
                "qq": user.qq,
                "phone": user.phone,
                "sex": user.sex
            }
        }
    except:
        db.session.rollback()
        resp = {
            "result_code": -1,
            "err_msg": "register error"
        }
    return jsonify(resp)

@bp.route('test/')
@login_required
def test():
    return jsonify({
        "result_code": 1
    })

@app.errorhandler(403)
def err403(e):
    return jsonify({
        "result_code": 403
    })

@app.errorhandler(405)
def err405(e):
    return jsonify({
        "result_code": 405
    })

@app.errorhandler(404)
def err404(e):
    return jsonify({
        "result_code": 404
    })

@app.errorhandler(500)
def err500(e):
    return jsonify({
        "result_code": 500
    })
