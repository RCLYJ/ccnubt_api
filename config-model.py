# coding: utf-8



class Confg(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    APPID = '小程序id'
    SECRET = '小程序secret key'
    MAIL_HOST = '邮件服务器地址'
    MAIL_USER = '邮件用户名'
    MAIL_PASS = '邮件密码'
    # 定时任务
    SCHEDULER_API_ENABLE = True
    JOBS = [
        {
            'id': 'job1',
            'func': 'ccnubt.scheduler:scheduler_task',
            'trigger': 'cron',
            'hour': '8',
        }
    ]

    # 需要显示文档的 Api
    API_DOC_MEMBER = ['user']

    # 需要排除的 RESTful Api 文档
    RESTFUL_API_DOC_EXCLUDE = []




class DevelopmentConfig(Confg):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    SECRET_KEY = ''


class ProductionConfig(Confg):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://'
    SECRET_KEY = ''


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}