import requests
from ccnubt import store
import json
from ccnubt.model import User, Reservation, db
from wsgi import app
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr

def send_msg(rid):
    with app.app_context():
        # print(User.query.all())
        token_url = 'https://api.weixin.qq.com/cgi-bin/token'
        token = store.get('access_token')
        if token:
            token = token.decode(encoding='utf-8')
        if not token:
            appid = app.config.get('APPID')
            secret = app.config.get('SECRET')
            res = requests.get(token_url, params={
                "grant_type": "client_credential",
                "appid": appid,
                "secret": secret
            })
            data = json.loads(res.text)
            print (res.text)
            try:
                token = data['access_token']
                store.set("access_token", token, 60 * 60 * 2)
            except:
                return
        # print('to')
        # print(token)
        r = Reservation.query.filter_by(id=rid).first()
        u = User.query.filter_by(id=r.user_id).first()
        bu = User.query.filter_by(id=r.bt_user_id).first()
        url = 'https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token=%s'
        url = url % token
        res = requests.post(url, json={
            "touser": u.openid,
            "template_id": "TkqGXhUoHMNbfIxjjTsDg3lSkoiGr4hQj_-eVyiAIeM",
            "form_id": r.formid,
            "data": {
                "keyword1": {
                    "value": str(r.id)
                },
                "keyword2": {
                    "value": bu.name
                },
                "keyword3": {
                    "value": bu.phone
                },
                "keyword4": {
                    "value": 'QQ:'+bu.qq
                }
            }
        })
        # print(res.text)




def send_email(rid):
    with app.app_context():
        r = Reservation.query.filter_by(id=rid).first()
        if r.formid == 'send':
            return
        # print(r)
        u = User.query.filter_by(id=r.user_id).first()
        bu = User.query.filter_by(id=r.bt_user_id).first()
        print(u)
        mail_host = app.config.get('MAIL_HOST')
        mail_user = app.config.get('MAIL_USER')
        mail_pass = app.config.get('MAIL_PASS')

        to_addr = u.qq+"@qq.com"
        from_addr = mail_user
        # from_addr = mail_user
        content = '''%s:
        您好！
        您的订单（订单号：%s, 维修状态： 维修%s）已经完成，请您对队员%s的服务做出评价。
        奔腾服务，竭诚为您！
        
        奔腾服务队
        ''' % (u.name, r.id, '成功' if r.solved else'失败', bu.name)
        h_from = '奔腾服务队<ccnubt@qq.com>'
        h_to = u.name+'<%s@qq.com>' % u.qq
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = Header(h_from, 'utf-8')
        msg['To'] = Header(h_to, 'utf-8')
        subject = '华中师范大学奔腾服务队维修反馈'
        msg['Subject'] = Header(subject, 'utf-8')

        try:
            smtp = smtplib.SMTP_SSL(mail_host)
            smtp.login(mail_user, mail_pass)
            print('login')
            smtp.sendmail(from_addr, to_addr, msg.as_string())
            r.formid = 'send'
            try:
                db.session.add(r)
                db.session.commit()
            except:
                db.session.rollback()
            print('success to send email to' + h_to)
        except:
            print('fail to send email to' + h_to)




