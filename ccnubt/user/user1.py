# coding: utf-8
from flask import jsonify, abort, request
from flask_login import login_required, current_user
from ..model import Reservation, User, db
from . import bp
from concurrent.futures import ThreadPoolExecutor
from .send_msg import send_msg
from sqlalchemy import desc,  func, and_
import random
from .. import store
from datetime import datetime


# 队员
# status: 0取消 1待接单 2已接单 3维修中 4完成，待确认 5已确认，待评价 6结束
# 接单status=2
@bp.route('order/<int:rid>/')
@login_required
def bt_order(rid):
    '''接单
@@@
### Param
rid: 订单表号
#### Return
```
{
    result_code: x,
    err_msg
}
```
##### Result_code
|result_code|err_msg|detail|
|-----|----|-----|
|1|success|成功|
|403| |没有权限|
|404| |订单不存在|
|-1|current status err|订单状态错误|
@@@
    '''
    if current_user.role < 1:
        abort(403)
    r = Reservation.query.filter_by(id=rid).first()
    if not r:
        abort(404)
    r.bt_user_id = current_user.id
    if r.status != 1:
        return jsonify({"result_code": -1, "err_msg": "current status err"})
    r.status = 2
    try:
        db.session.add(r)
        db.session.commit()
    except:
        abort(500)
    with ThreadPoolExecutor(1) as executor:
        t = executor.submit(send_msg, rid=rid)
        # print(t.result())
    return jsonify({
        "result_code": 1,
        "err_msg": "sucess"
    })


# 维修status=3
@bp.route('repair/<int:rid>/')
@login_required
def bt_repair(rid):
    '''改为维修中状态
@@@
#### Param
rid:订单编号
#### Return
```
{
    result_code:  x,
    err_msg: x
```
##### result_code
|result_code|err_msg|detail|
|----------|----|-------|
|1|success|成功|
|404| |订单不存在|
|403| |没有权限,非队员或非本人接单|
|-1|current status err|当前订单状态错误|
@@@
    '''
    r = Reservation.query.filter_by(id=rid).first()
    if not r:
        abort(404)
    if current_user.role < 1 or r.bt_user_id != current_user.id:
        abort(403)
    if r.status != 2:
        return jsonify({"result_code": -1, "err_msg": "current status err"})
    r.status = 3
    try:
        db.session.add(r)
        db.session.commit()
    except:
        abort(500)
    return jsonify({"result_code": 1, "err_msg": "success"})


# 完成,已修好 status=4
@bp.route('finish/<int:rid>/')
@login_required
def bt_finish(rid):
    '''维修完成
@@@
#### Args
|参数|内容|
|---|----|
|api_key|api_key|
|rid|订单编号|
|solved|true解决, false未解决(默认)|
#### Return
```
{
    result_code: 状态码,
    err_msg: 错误信息
}
```
##### result_code
|code|err_msg|detail|
|--|---|---|
|1|success|成功｜
|404|  |订单不存在|
|403|  |没有权限|
|-1|current status err|当前状态错误|

@@@
    '''
    s = request.args.get('solved')
    solved = False
    if s == 'true':
        solved = True
    r = Reservation.query.filter_by(id=rid).first()
    if not r:
        abort(404)
    if current_user.role < 1 or r.bt_user_id != current_user.id:
        abort(403)
    if r.status != 3:
        return jsonify({
            "result_code": -1,
            "err_msg": "current status err"
        })
    r.status = 4
    r.solved = solved
    r.finish_time = datetime.utcnow()
    try:
        db.session.add(r)
        db.session.commit()
    except:
        abort(500)
    return jsonify({
        "result_code": 1,
        "err_msg": "success"
    })

# # 失败完成 status=4
# @bp.route('unfinish/<int:rid>/')
# @login_required
# def un_finish(rid):
#     r = Reservation.query.filter_by(id=rid).first()
#     if not r:
#         abort(404)
#     if current_user.role < 1 or r.bt_user_id != current_user.id:
#         abort(403)
#     if r.status != 3:
#         return jsonify({
#             "result_code": -1,
#             "err_msg": "current status err"
#         })
#     r.status = 4
#     r.solved = False
#     try:
#         db.session.add(r)
#         db.session.commit()
#     except:
#         abort(500)
#     return jsonify({
#         "result_code": 1,
#         "err_msg": "sucess"
#     })


# 未接订单
@bp.route('unorder/')
@login_required
def bt_unorder_reservations():
    '''查看未接订单
@@@
#### Return
```
{
    result_code: 1,
    reservations: [{
        id: 订单编号,
        detail: 问题描述,
        create_time: 创建时间,
        user_info: {
            name: 姓名,
            sex: 性别,
            phone: 手机,
            qq: QQ号码
        }
    },
    ....]
}
```
@@@
    '''
    if current_user.role < 1:
        abort(403)
    rs = Reservation.query.filter_by(status=1)
    res = []
    for r in rs:
        u = User.query.filter_by(id=r.user_id).first()
        res.append({
            "user_info":{
                "name": u.name,
                "sex": u.sex,
                "phone": u.phone,
                "qq": u.qq
            },
            "id": r.id,
            "detail": r.detail,
            "create_time": r.create_time
        })
    return jsonify({
        "result_code": 1,
        "reservations": res
    })


@bp.route('myorder/')
@login_required
def bt_ordered_reservation():
    '''查看已接订单
@@@
#### Return

@@@
    '''
    if current_user.role < 1:
        abort(403)
    rs = db.session.query(Reservation).filter_by(bt_user_id=current_user.id).order_by(desc(Reservation.id)).all()
    r_data = []

    for r in rs:
        u = User.query.filter_by(id=r.user_id).first()
        info = {
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
            "user_info": info
        })
    return jsonify({
        "result_code": 1,
        "reservations": r_data
    })

# 生成接单码
@bp.route('mycode/')
def bt_code():
    code = request.args.get("code")
    # print(code)
    if code:
        store.delete(code)
    if current_user.role != 1:
        abort(403)
    code = "".join(random.sample("123456789", 6))
    store.set(code, current_user.id, 60*5)
    if current_user.role != 1:
        abort(403)
    return jsonify({
        "result_code": 1,
        "code": code
    })


@bp.route('transfer/<int:id>/')
def bt_transfer(id):
    u = current_user
    id = int(id)
    if u.role != 1:
        abort(403)
    r = Reservation.query.filter_by(id=id).first()
    # print(id)
    if not r or r.bt_user_id != u.id:
        abort(404)
    code = "".join(random.sample("0123456789", 8))
    store.set(code, r.id, 60 * 5)
    return jsonify({
        "result_code": 1,
        "code": code
    })


@bp.route('receive/')
def bt_receive():
    u = current_user
    if u.role != 1:
        abort(403)
    code = request.args.get("code")
    rid = store.get(code)
    if not code or not rid:
        abort(404)
    r = Reservation.query.filter_by(id=int(rid)).first()
    r.bt_user_id = u.id
    store.delete(code)
    try:
        db.session.add(r)
        db.session.commit()
    except:
        db.session.rollback()
        abort(500)
    return jsonify({
        "result_code": 1
    })

@bp.route('summary/')
def bt_summary():
    '''查看队员排名
@@@
#### Return
```
{
    result_code: 1,
    data: [{
        name: 队员姓名,
        avg_score: 平均分,
        count: 接单量,
        score: 综合分
        },
        ...
    ]
}
```
@@@
    '''
    today = datetime.today()
    first_day = datetime(today.year, today.month, 1, 0, 0, 0)
    sub = db.session.query(Reservation).\
        filter(and_(Reservation.create_time>=first_day, Reservation.status==6)).subquery()
    rs = db.session.query(sub.c.bt_user_id, User.name,func.count('*'), func.avg(sub.c.score)).\
        join(User, User.id==sub.c.bt_user_id).\
        group_by(User.id).all()
    # print(rs)
    data = []
    m = 0
    for r in rs:
         m = max(m, r[2])
    for r in rs:
        data.append({
            "name": r[1],
            "avg_score": round(float(r[3]),2),
            "count": r[2],
            "score": round(r[2]/m *50 + float(r[3])*10.0, 2)
        })
    if data:
        data.sort(key=lambda obj: (obj.get("score")),reverse=True)
    return jsonify({
        "result_code": 1,
        "data": data
    })
