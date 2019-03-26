from .model import db, Reservation, User
from .user.send_msg import send_email
from sqlalchemy import and_
import datetime
from wsgi import app

def scheduler_task():
    with app.app_context():
        print("scheduler_task: "+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        date = datetime.datetime.now() - datetime.timedelta(days=4)
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


