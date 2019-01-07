from flask import Flask
from ccnubt import db, login_manager
from config import config

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

if __name__ == '__main__':
    app.run()
