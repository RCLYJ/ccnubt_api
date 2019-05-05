from .model import db, Reservation, User
from .user.send_msg import send_email, send_msg
from sqlalchemy import and_
import datetime
from wsgi import app
import random
from concurrent.futures import ThreadPoolExecutor

def scheduler_task():
    with app.app_context():
        print("scheduler_task: "+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        date = datetime.datetime.now() - datetime.timedelta(days=2)
        rs = Reservation.query.\
            filter(and_(Reservation.formid == 'send', Reservation.finish_time <= date,
                                           Reservation.status >= 4, Reservation.status < 6)).all()
        for r in rs:
            r.status = 6
            r.score = 5
            r.evaluation = '系统自动好评'
            try:
                db.session.add(r)
                db.session.commit()
                print('自动好评 rid=' + str(r.id))
            except:
                db.session.rollback()

        rs = Reservation.query.\
            filter(and_(Reservation.formid != 'send', Reservation.status >= 4, Reservation.status < 6)).all()
        # print(rs)
        for r in rs:
            send_email(r.id)

        # 自动分配订单
        date = datetime.datetime.now() - datetime.timedelta(hours=2)
        rs = Reservation.query.\
            filter(and_(Reservation.status == 1, Reservation.create_time <= date)).all()
        bt = User.query.\
            filter(User.role == 1).all()
        for r in rs:
            b = bt[random.randint(0, len(bt)-1)]
            r.status = 2
            r.bt_user_id = b.id
            db.session.add(r)
            db.session.commit()
            print("分配订单%d 给 %s" % (r.id, b.name))
            # try:
            #     db.session.add(r)
            #     db.session.commit()
            #     print("分配订单%d 给 %s" % (r.id, b.name))
            #     # send_msg(r.id)
            #     # with ThreadPoolExecutor(1) as executor:
            #     #     t = executor.submit(send_msg, rid=rid)
            #     #     print(r.result())
            #
            # except:
            #     db.session.rollback()




