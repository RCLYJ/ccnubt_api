# coding:utf-8
from flask import Blueprint, jsonify, request, abort
from .model import User, Reservation
from flask_login import login_required, login_user, current_user
import json, os, hashlib
from . import store, db
bp = Blueprint('root', __name__, url_prefix='/root')


@bp.route('login/', methods=['POST'])
def root_login():
    json_data = json.loads(request.data)
    username = json_data.get('username')
    password = json_data.get('password')

    u = User.query.filter_by(openid=username).first()
    if not u or u.api_key != password or u.role != 10:
        abort(403)
    api_key = hashlib.md5(os.urandom(64)).hexdigest()
    print(api_key)
    store.set(api_key, username)
    return jsonify({
        "result_code": 1,
        "msg": "login sucess",
        "api_key": api_key
    })


@bp.route('user/')
@login_required
def root_user():
    if current_user.role != 10:
        return {
            "result_code": -1,
            "err_msg": 'permission denied'
        }
    users = User.query.filter(User.role != 10).all()
    user_list = []
    for u in users:
        user_list.append({
            "id": u.id,
            "name": u.name,
            "sex": u.sex,
            "phone": u.phone,
            "qq": u.qq,
            "last_active_time": u.last_active_time,
            "active": u.active,
            "role": u.role
        })
    return jsonify({
        "result_code": 1,
        "users_list": user_list
    })


@bp.route('user/active/<int:id>/')
@login_required
def root_active_user(id):
    if current_user.role != 10:
        abort(403)
    u = User.query.filter_by(id=id).first()
    if not u:
        abort(404)
    u.active = not u.active
    db.session.add(u)
    db.session.commit()
    return jsonify({
        "result_code": 1
    })

@bp.route('user/role/')
def auth_role():
    if current_user.role != 10:
        abort(403)
    id = request.args.get('id')
    role = request.args.get('role')
    print(id, role)
    if not id or not role:
        abort(404)
    u = User.query.filter_by(id=id).first()
    if not u:
        abort(404)
    u.role = role
    db.session.add(u)
    db.session.commit()
    return jsonify({
        "result_code": 1
    })

@bp.route('reservation/')
@login_required
def root_reservation():
    if current_user.role != 10:
        abort(403)
    rs = db.session.query(Reservation).all()
    r_data = []

    for r in rs:
        u = User.query.filter_by(id=r.user_id).first()
        info = {
            "name": u.name,
            "sex": u.sex,
            "phone": u.phone,
            "qq": u.qq
        }
        bt_info = 0
        if r.bt_user_id:
            u = User.query.filter_by(id=r.bt_user_id).first()
            bt_info = {
                "name": u.name,
                "sex": u.sex,
                "phone": u.phone,
                "qq": u.qq
            }
        r_data.append({
            "id": r.id,
            "status": r.status,
            "detail": r.detail,
            "create_time": r.create_time,
            "finish_time": r.finish_time,
            "score": r.score,
            "evaluation": r.evaluation,
            "solved": r.solved,
            "user_info": info,
            "bt_user_info": bt_info
        })
    return jsonify({
        "result_code": 1,
        "reservations": r_data
    })