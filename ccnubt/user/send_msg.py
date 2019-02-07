import requests
from ccnubt import store
import json
from ccnubt.model import User, Reservation
from wsgi import app

def send_msg(rid):
    with app.app_context():
        print(User.query.all())
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
        print('to')
        print(token)
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
                    "value": bu.qq
                }
            }
        })
        print(res.text)



