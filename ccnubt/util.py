from . import store
import os, hashlib
from flask_cli import AppGroup
from .model import User, db
import click
import xlwt

admin_cmd = AppGroup('admin')



@admin_cmd.command('add')
def add_admin_url():
    token = hashlib.md5(os.urandom(64)).hexdigest()
    store.set("addadmin"+token, "true", 60*60)
    base_url = 'https://ccnubt.club/#/newadmin'
    # base_url = 'http://127.0.0.1:8080/#/newadmin'
    print(base_url+'?token='+token)


@admin_cmd.command('list')
def admin_list():
    us = User.query.filter(User.role==10).all()
    for u in us:
        print("id:%s name: %s active:%s" % (u.id, u.name, u.active))


@admin_cmd.command('verify')
@click.argument('id')
def admin_verify(id):
    # print(id)
    u = User.query.filter(User.id==int(id)).first()
    if not u or u.role != 10:
        print('user does not exist')
    u.active = not u.active
    try:
        db.session.add(u)
        db.session.commit()
    except:
        db.rollback()
        print('fail')
    print('success')


@admin_cmd.command('export_user')
def export_user():
    us = User.query.filter(User.enable == True).all()
    workbook = xlwt.Workbook(encoding='ascii')
    worksheet = workbook.add_sheet('用户')
    row0 = ['id', '姓名', '性别', '手机号码', 'QQ']
    for i in range(0,len(row0)):
        worksheet.write(0, i, row0[i])
    for i in range(0, len(us)):
        worksheet.write(i + 1, 0, us[i].id)
        worksheet.write(i + 1, 1, us[i].name)
        worksheet.write(i + 1, 2, '男' if (us[i].sex == 'male') else '女')
        worksheet.write(i + 1, 3, us[i].phone)
        worksheet.write(i + 1, 4, us[i].qq)
    workbook.save('user.xls')
    print('ok')
