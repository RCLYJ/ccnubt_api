# coding: utf-8
from flask import jsonify, request, json, abort
from flask_login import login_required, current_user
from ..model import Reservation, User
from .. import db
from datetime import datetime
from . import bp
from sqlalchemy import and_


# status: -1取消 0待接单 1已接单 2维修中 3维修完成 4失败 5已确认，待评价 6结束
@bp.route('reserve/', methods=['POST'])
@login_required
def new_reservation():
    json_data = json.loads(request.data)
    uid = current_user.id
    r = Reservation.query.filter_by(user_id=uid).\
        filter(and_(Reservation.status < 6, Reservation.status >= 0)).first()
    if r:
        return jsonify({
            "result_code": 2,
            "err_msg": "exist reservation unfinished"
        })
    r = Reservation()
    r.user_id = current_user.id
    r.detail = json_data.get("detail")
    r.status = 0
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
        "msg": "sucess"
    })

# 取消订单 status=-1
@bp.route('cancel/<int:rid>/')
@login_required
def cancel_reservation(rid):
    r = Reservation.query.filter_by(id=rid).first()
    if not r or r.user_id != current_user.id:
        abort(403)
    if r.status > 1:
        return jsonify({
            "result_coe": -1,
            "err_msg": "can not cancel"
        })
    r.status = -1
    db.session.add(r)
    db.session.commit()
    return jsonify({
        "result_code": 1,
        "msg": "cancel sucessfully"
    })

# 确认 status=5
@bp.route('confirm/<int:rid>/')
@login_required
def confirm_reservation(rid):
    r = Reservation.query.filter_by(id=rid).first()
    if not r or r.user_id != current_user.id:
        abort(403)
    if r.status not in (3,4):
        return jsonify({
            "result_coe": -1,
            "err_msg": "can not confirm"
        })
    r.status = 5
    r.finish_time = datetime.utcnow()
    db.session.add(r)
    db.session.commit()
    return jsonify({
        "result_code": 1,
        "msg": "confirm sucessfully"
    })


# 确认 status=6
'''
{
  "score": ,
  "reservation": 
}
'''

@bp.route('evaluate/<int:rid>/', methods=['POST'])
@login_required
def evaluate_reservation(rid):
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
        return jsonify({
            "result_code": -1,
            "err_msg": "invalid data"
        })
    return jsonify({
        "result_code": 1,
        "msg": "evaluation sucessfully"
    })

@bp.route('myreservation/')
@login_required
def my_reservation():
    id = current_user.id
    rs = db.session.query(Reservation).filter_by(user_id=id).order_by('-id').all()
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



