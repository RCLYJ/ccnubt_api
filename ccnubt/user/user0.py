# coding: utf-8
from flask import jsonify, request, json, abort
from flask_login import login_required, current_user
from ..model import Reservation, User, Activity, db
from datetime import datetime, timedelta
from . import bp
from sqlalchemy import and_, desc
from ccnubt import store
import random

# status: 0取消 1待接单 2已接单 3维修中 4完成，待确认 5已确认，待评价 6结束
@bp.route('reserve/', methods=['POST'])
@login_required
def new_reservation():
    '''新订单
@@@
## Arg:
    api_key: api_key
## Data:
```
{
    detail: 问题描述,
    formid: 小程序formid
}
```
## Return
```
{
    result_code: 状态码,
    err_msg: 错误信息
}
```
### result_code
|code|err_msg|detail|
|--|---|---|
|1|success|成功|
|2|exist unfinished reservation|存在未完成订单|
|-1|invalid data|数据不合法|
@@@
    '''
    json_data = json.loads(request.data)
    uid = current_user.id
    # 查看是否有未完成订单
    r = Reservation.query.filter_by(user_id=uid).\
        filter(and_(Reservation.status < 6, Reservation.status > 0)).first()
    if r:
        return jsonify({
            "result_code": 2,
            "err_msg": "exist unfinished reservation"
        })
    # 添加订单
    r = Reservation()
    r.user_id = current_user.id
    r.detail = json_data.get("detail")
    r.formid = json_data.get("formid")
    r.status = 1
    try:
        db.session.add(r)
        db.session.commit()
    except:
        return jsonify({
            "result_code": -1,
            "err_msg": "invalid data"
        })

    return jsonify({
        "result_code": 1,
        "err_msg": "sucess"
    })

# 取消订单 status=0
@bp.route('cancel/<int:rid>/')
@login_required
def cancel_reservation(rid):
    '''取消订单
@@@
## Arg:
    api_key: api_key


## Return
```
{
    result_code: 状态码,
    err_msg: 错误信息
}
```
### result_code
|code|err_msg|detail|
|--|---|---|
|1|success|成功|
|403| |用户不是订单所有者|
|401| |用户被禁用|
|-1|can not cancel|当前订单不可取消|
@@@
    '''
    r = Reservation.query.filter_by(id=rid).first()
    if not r or r.user_id != current_user.id:
        abort(403)
    if r.status != 1:
        return jsonify({
            "result_coe": -1,
            "err_msg": "can not cancel"
        })
    r.status = 0
    db.session.add(r)
    db.session.commit()

    # 一天内超过10个取消订单,禁用用户
    d = datetime.utcnow() - timedelta(days=1)
    rc = Reservation.query.filter_by(user_id=current_user.id).\
            filter(and_(Reservation.create_time >= d, Reservation.status == 0)).count()
    ##print(rc)
    if rc >= 10:
        u = current_user
        u.active = False
        try:
            db.session.add(u)
            db.session.commit()
        except:
            db.session.rollback()
            abort(500)
        abort(401)

    return jsonify({
        "result_code": 1,
        "err_msg": "success"
    })

# 确认 status=5
@bp.route('confirm/<int:rid>/')
@login_required
def confirm_reservation(rid):
    '''确认订单
@@@
## Param
rid: 订单号
## Return
```
{
    result_code: 状态码,
    err_msg: 错误信息
}
```
### result_code
|code|err_msg|detail|
|--|---|---|
|1|success|成功取消|
|-1|can not confirm|订单状态错误,不能取消|
@@@
    '''
    r = Reservation.query.filter_by(id=rid).first()
    if not r or r.user_id != current_user.id:
        abort(403)
    if r.status != 4:
        return jsonify({
            "result_code": -1,
            "err_msg": "can not confirm"
        })
    r.status = 5
    r.finish_time = datetime.utcnow()
    db.session.add(r)
    db.session.commit()
    return jsonify({
        "result_code": 1,
        "err_msg": "success"
    })


# 评价 status=6
@bp.route('evaluate/<int:rid>/', methods=['POST'])
@login_required
def evaluate_reservation(rid):
    '''评价
@@@
## Param
rid: 订单号
## Data(json)
```
{
    "score": 分数(int),
    "evaluation: 评价(string)
}
```

## Return
```
{
    result_code: 状态码,
    err_msg: 错误信息
}
```
### result_code
|code|err_msg|detail|
|--|---|---|
|1|success|评价成功|
|-1|can not evaluate|订单状态错误,不能评价|
@@@
    '''
    json_data = json.loads(request.data)
    r = Reservation.query.filter_by(id=rid).first()
    if not r or r.user_id != current_user.id:
        abort(403)
    if r.status != 5:
        return jsonify({
            "result_code": -1,
            "err_msg": "can not evaluate"
        })
    r.status = 6
    r.score = json_data.get("score")
    r.evaluation = json_data.get("evaluation")
    try:
        db.session.add(r)
        db.session.commit()
    except:
        db.session.rollback()
        abort(500)
    return jsonify({
        "result_code": 1,
        "err_msg": "success"
    })

@bp.route('myreservation/')
@login_required
def user_reservation():
    '''用户查看订单
@@@
## Return
```
{
    "result_code": 1,
    "evaluations": [
        {
            "create_time": "工单创建时间",
            "detail": "问题描述",
            "evaluation": "用户评价",
            "finish_time": "用户确认完成时间",
            "id": 工单号,
            "status": 工单状态,
            "score": 评分,
            "bt_info": null 或 {
                "name": "xxx",
                "phone": "xxx",
                "qq": "xxx",
                "sex": "male"/"female"
            }
        },
        .....
    ]
}
```
@@@
    '''
    id = current_user.id
    rs = db.session.query(Reservation).filter_by(user_id=id).order_by(desc(Reservation.id)).all()
    r_data = []

    for r in rs:
        u = User.query.filter_by(id=r.bt_user_id).first()
        info = None
        if u:
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
            "bt_info": info
        })
    return jsonify({
        "result_code": 1,
        "reservations": r_data
    })

@bp.route('activity/')
@login_required
def activity():
    '''查看活动
@@@
## Return
```
{
    result_code: 1,
    activities: [{
        title: 活动名,
        start_time: 开始时间,
        end_time: 结束时间,
        content: 内容,
        pos: 地点
    },
    ...
    ]
}
```
@@@
    '''
    now = datetime.utcnow()
    a = Activity.query.filter(Activity.end_time >= now).order_by(desc(Activity.id)).all()
    acs = []
    for t in a:
        acs.append({
            "title": t.title,
            "start_time": t.start_time,
            "end_time": t.end_time,
            "content": t.content,
            "pos": t.pos
        })
    return jsonify({
        "result_code": 1,
        "activities": acs
    })


@bp.route('reservecode/', methods=['GET', 'POST'])
def reserve_code():
    if request.method == 'POST':
        json_data = json.loads(request.data)
        code = json_data.get("code")
        detail = json_data.get("detail")
        if not code:
            abort(404)
        bt_uid = store.get(code)
        if not bt_uid:
            abort(404)
        bt_uid = int(bt_uid)
        r = Reservation()
        r.status = 1
        r.bt_user_id = bt_uid
        r.detail = detail
        r.user_id = current_user.id
        try:
            db.session.add(r)
            db.session.commit()
        except:
            db.session.rollback()
            abort(500)
        return jsonify({
            "result_code": 1
        })
    code = request.args.get("code")
    if not code:
        abort(404)
    bt_uid = store.get(code)
    if not bt_uid:
        abort(404)
    bt_uid = int(bt_uid)
    bu = User.query.filter_by(id=bt_uid).first()
    if not bu:
        abort(404)
    store.delete(code)
    code = "".join(random.sample('qwertyuioplkjhgfdsazxcvbnm',8))
    store.set(code, bt_uid, 60*60)
    return jsonify({
        "result_code": 1,
        "code": code,
        "bt_info": {
            "name": bu.name,
            "sex": bu.sex
        }
    })
