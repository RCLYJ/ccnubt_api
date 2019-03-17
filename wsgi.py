from flask import Flask
from ccnubt import login_manager
from config import config
from ccnubt.model import db
from flask_docs import ApiDoc
from ccnubt.util import admin_cmd
from flask_apscheduler.scheduler import APScheduler


app = Flask(__name__)

from ccnubt import auth
app.register_blueprint(auth.bp)

from ccnubt import user
app.register_blueprint(user.bp)

from ccnubt import root
app.register_blueprint(root.bp)

app.config.from_object(config['development'])
# app.config.from_object(config['production'])

db.init_app(app)
login_manager.init_app(app)

ApiDoc(app)

app.cli.add_command(admin_cmd)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

if __name__ == '__main__':

    app.run()

