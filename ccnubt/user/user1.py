# coding: utf-8
from flask import jsonify, abort
from flask_login import login_required, current_user
from ..model import Reservation, User
from .. import db
from . import bp

# 队员
# 接单status=1
@bp.route('order/<int:rid>/')
@login_required
def order(rid):
    if current_user.role < 1:
        abort(403)
    r = Reservation.query.filter_by(id=rid).first()
    if not r:
        abort(404)
    r.bt_user_id = current_user.id
    if r.status != 0:
        return jsonify({"result_code": -1, "err_msg": "current status err"})
    r.status = 1
    try:
        db.session.add(r)
        db.session.commit()
    except:
        abort(500)
    return jsonify({
        "result_code": 1,
        "err_msg": "sucess"
    })


# 维修status=2
@bp.route('repair/<int:rid>/')
@login_required
def repair(rid):
    r = Reservation.query.filter_by(id=rid).first()
    if not r:
        abort(404)
    if current_user.role < 1 or r.bt_user_id != current_user.id:
        abort(403)
    if r.status != 1:
        return jsonify({"result_code": -1, "err_msg": "current status err"})
    r.status = 2
    try:
        db.session.add(r)
        db.session.commit()
    except:
        abort(500)
    return jsonify({"result_code": 1, "err_msg": "sucess"})

# 完成 status=3
@bp.route('finish/<int:rid>/')
@login_required
def finish(rid):
    r = Reservation.query.filter_by(id=rid).first()
    if not r:
        abort(404)
    if current_user.role < 1 or r.bt_user_id != current_user.id:
        abort(403)
    if r.status != 2:
        return jsonify({
            "result_code": -1,
            "err_msg": "current status err"
        })
    r.status = 3
    r.solved = True
    try:
        db.session.add(r)
        db.session.commit()
    except:
        abort(500)
    return jsonify({
        "result_code": 1,
        "err_msg": "sucess"
    })

# 失败完成 status=
@bp.route('unfinish/<int:rid>/')
@login_required
def un_finish(rid):
    r = Reservation.query.filter_by(id=rid).first()
    if not r:
        abort(404)
    if current_user.role < 1 or r.bt_user_id != current_user.id:
        abort(403)
    if r.status != 2:
        return jsonify({
            "result_code": -1,
            "err_msg": "current status err"
        })
    r.status = 4
    r.solved = False
    try:
        db.session.add(r)
        db.session.commit()
    except:
        abort(500)
    return jsonify({
        "result_code": 1,
        "err_msg": "sucess"
    })


# 未接订单
@bp.route('unorder/')
@login_required
def unerder_reservations():
    if current_user.role < 1:
        abort(403)
    rs = Reservation.query.filter_by(status=0)
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
def my_ordered_reservation():
    if current_user.role < 1:
        abort(403)
    rs = db.session.query(Reservation).filter_by(bt_user_id=current_user.id).order_by('-id').all()
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
