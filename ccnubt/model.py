# coding: utf-8
from . import db, login_manager, store
from flask_login import UserMixin
from datetime import datetime


'''
用户信息
role
'''


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role = db.Column(db.Integer, nullable=False, default=0)
    api_key = db.Column(db.String(128), nullable=True)
    openid = db.Column(db.String(64), nullable=False, unique=True)
    # userinfo
    name = db.Column(db.String(20), nullable=True)
    sex = db.Column(db.Enum('male', 'female'), nullable=True )
    phone = db.Column(db.String(20), nullable=True)
    qq = db.Column(db.String(20), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    enable = db.Column(db.Boolean, nullable=False, default=False)
    last_active_time = db.Column(db.DateTime)
    def is_active(self):
        return self.active

    def get_id(self):
        return self.id


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.args.get('api_key')
    if api_key:
        openid = store.get(str(api_key))
        if not openid:
            return None
        openid = openid.decode('utf-8')
        user = User.query.filter_by(openid=openid).first()
        # print(user)
        if user:
            return user
    api_key = request.headers.get('Authorization')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            if not user.active:
                return False
            return user
    return None


'''
预约
status: -1取消 0待接单 1已接单 2维修中 3维修完成 4已确认，待评价 5完成
'''


class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.Integer, default=0, nullable=False)
    detail = db.Column(db.Text, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    finish_time = db.Column(db.DateTime, nullable=True)
    bt_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    score = db.Column(db.Integer, default=0, nullable=True)
    evaluation = db.Column(db.Text, nullable=True)
    solved = db.Column(db.Boolean, default=False)

