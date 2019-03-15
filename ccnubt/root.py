# coding:utf-8
from flask import Blueprint, jsonify, request, abort, make_response, send_from_directory
from .model import User, Reservation, Activity,db
from flask_login import login_required, login_user, current_user
import json, os, hashlib
from datetime import datetime
from . import store
from sqlalchemy import desc, and_, func
import xlwt
from concurrent.futures import ThreadPoolExecutor
from .user.send_msg import send_email


bp = Blueprint('root', __name__, url_prefix='/root')



@bp.route('login/', methods=['POST'])
def root_login():
    json_data = json.loads(request.data)
    username = json_data.get('username')
    password = json_data.get('password')
    u = User.query.filter_by(openid=username).first()

    hash_password = hashlib.md5(password.encode('utf8')).hexdigest()
    if not u or u.api_key != hash_password or u.role != 10 or not u.active:
        abort(403)
    api_key = hashlib.md5(os.urandom(64)).hexdigest()
    # print(api_key)
    store.set(api_key, username, 60*60)
    return jsonify({
        "result_code": 1,
        "msg": "login success",
        "api_key": api_key
    })


@bp.route('addadmin/', methods=['post'])
def root_add_admin():
    json_data = json.loads(request.data)
    token = "addadmin" + request.args.get('token')
    if not token or not store.get(token):
        abort(403)
    store.delete(token)
    username = json_data.get("username")
    password = json_data.get("password")
    name = json_data.get("name")
    if User.query.filter(User.openid == username).all():
        return jsonify({
            "result_code": 403,
            "err_msg": 'username exists'
        })
    u = User()
    u.openid = username
    u.api_key = hashlib.md5(password.encode('utf8')).hexdigest()
    u.role = 10
    u.name = name
    u.active = False
    u.enable = 1
    print(u)
    try:
        db.session.add(u)
        db.session.commit()
    except:
        db.session.rollback()
        abort(500)
    return jsonify({
        "result_code": 1,
        "err_msg": "success"
    })


@bp.route('user/')
@login_required
def root_user():
    if current_user.role != 10:
        abort(403)
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    try:
        role = int(request.args.get('role'))
    except:
        role = 3
    pagesize = 20
    role_set = [0,1] if role==3 else [role,]
    us = User.query.filter(and_(User.role.in_(role_set), User.enable==True))
    users = us.limit(pagesize).offset(pagesize * (page - 1))
    total = us.count()
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
        "users_list": user_list,
        "total": total
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
    # print(id, role)
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

@bp.route('user/sendmail/')
def root_send_mail():
    # print('send')
    if current_user.role != 10:
        abort(403)
    rid = request.args.get('rid')
    # print('rid')
    # print(rid)
    try:
        rid = int(rid)
    except:
        abort(404)
    with ThreadPoolExecutor(1) as executor:
        t = executor.submit(send_email, rid=rid)
        # print(t.result())
    return jsonify({
        "result_code": 1,
        "err_msg": 'success'
    })

# @bp.route('user/del/')
# def root_user_disable():
#     if current_user.role != 10:
#         abort(403)
#     id = request.args.get('id')
#     if not id:
#         abort(404)
#     u = User.query.filter_by(id=id).first()
#     print(u)
#     if not u:
#         abort(404)
#
#     rs = Reservation.query.filter_by(user_id=id).all()
#     db.session.delete(rs)
#     db.session.delete(u)
#     db.session.commit()
#     # try:
#     #     db.session.delete(rs)
#     #     db.session.delete(u)
#     #     db.session.commit()
#     # except:
#     #     db.session.rollback()
#     #     abort(500)
#     return jsonify({
#         "result_code": 1
#     })


@bp.route('reservation/')
@login_required
def root_reservation():
    if current_user.role != 10:
        abort(403)
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    try:
        d_from = datetime.fromtimestamp(int(request.args.get("from"))//1000)
        d_to = datetime.fromtimestamp(int(request.args.get("to"))//1000)
    except:
        d_from = datetime.fromtimestamp(0)
        d_to = datetime.now()
    pagesize = 20
    rs = Reservation.query.filter(and_(Reservation.create_time>=d_from, Reservation.create_time<=d_to))
    rs_data = rs.order_by(desc(Reservation.id)).limit(pagesize).offset(pagesize*(page-1)).all()
    total = rs.count()
    r_data = []
    # print(rs_data)
    for r in rs_data:
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
            "bt_user_info": bt_info,
            "formid": r.formid
        })
    # time.sleep(3)
    return jsonify({
        "result_code": 1,
        "reservations": r_data,
        "total": total
    })


@bp.route('new_activity/', methods=['POST'])
@login_required
def root_add_activity():
    if current_user.role != 10:
        abort(403)
    json_data = json.loads(request.data)
    # print(json_data)
    try:
        title = json_data.get("title")
        content = json_data.get("content")
        start_time = json_data.get("start_time")
        end_time = json_data.get("end_time")
        pos = json_data.get("pos")
        id = json_data.get('id')
    except:
        abort(404)
    if id:
        a = Activity.query.filter_by(id=id).first()
    else:
        a = Activity()
    a.title = title
    a.content = content
    a.pos = pos
    a.start_time = datetime.utcfromtimestamp(start_time/1000)
    a.end_time = datetime.utcfromtimestamp(end_time/1000)
    try:
        db.session.add(a)
        db.session.commit()
    except:
        db.session.rollback()
        abort(500)
    return jsonify({
        "result_code": 1
    })

@bp.route('activity/del/<int:id>/')
@login_required
def root_del_activity(id):
    if current_user.role != 10:
        abort(403)
    a = Activity.query.filter_by(id=id).first()
    if not a:
        abort(404)
    try:
        db.session.delete(a)
        db.session.commit()
    except:
        db.session.rollback()
        abort(500)
    return jsonify({
        "result_code": 1
    })

@bp.route('activity/')
@login_required
def activity():
    now = datetime.utcnow()
    a = Activity.query.order_by(desc(Activity.start_time)).all()
    acs = []
    for t in a:
        acs.append({
            "title": t.title,
            "start_time": t.start_time,
            "end_time": t.end_time,
            "content": t.content,
            "pos": t.pos,
            "id": t.id
        })
    return jsonify({
        "result_code": 1,
        "activities": acs
    })

@bp.route('summary/')
@login_required
def root_summary():
    try:
        d_from = request.args.get('from')
        d_to = request.args.get('to')
        first_day = datetime.fromtimestamp(int(d_from)//1000)
        last_day = datetime.fromtimestamp(int(d_to)//1000)
    except:
        abort(403)

    sub = db.session.query(Reservation).filter(
        and_(Reservation.create_time >= first_day, Reservation.create_time<=last_day,Reservation.status == 6)).subquery()
    rs = db.session.query(sub.c.bt_user_id, User.name, func.count('*'), func.avg(sub.c.score)). \
        join(User, User.id == sub.c.bt_user_id). \
        group_by(User.id).all()

    # time.sleep(3)
    data = []
    m = 0
    for r in rs:
        m = max(m, r[2])
    for r in rs:
        data.append({
            "name": r[1],
            "avg_score": round(float(r[3]), 2),
            "count": r[2],
            "score": round(r[2] / m * 50 + float(r[3]) * 10.0, 2)
        })
    if data:
        data.sort(key=lambda obj: (obj.get("score")), reverse=True)
    return jsonify({
        "result_code": 1,
        "data": data
    })

@bp.route('export/user/')
@login_required
def root_export_user():
    if current_user.role != 10:
        abort(403)
    us = User.query.filter(and_(User.enable == True, User.role!=10)).order_by(desc(User.role)).all()
    workbook = xlwt.Workbook(encoding='utf8')
    worksheet = workbook.add_sheet('用户')
    row0 = ['id', '姓名', '性别', '手机号码', 'QQ', '角色']
    for i in range(0, len(row0)):
        worksheet.write(0, i, row0[i])
    for i in range(0, len(us)):
        worksheet.write(i + 1, 0, us[i].id)
        worksheet.write(i + 1, 1, us[i].name)
        worksheet.write(i + 1, 2, '男' if (us[i].sex == 'male') else '女')
        worksheet.write(i + 1, 3, us[i].phone)
        worksheet.write(i + 1, 4, us[i].qq)
        worksheet.write(i + 1, 5, '用户' if(not us[i].role) else '队员')
    workbook.save('/tmp/user.xls')
    resp = make_response(send_from_directory('/tmp', 'user.xls', as_attachment=True))
    resp.headers["Content-Type"] = 'application/x-download;charset=utf-8'
    resp.headers["Content-Disposition"] = "attachment; filename=user.xls"
    return resp
