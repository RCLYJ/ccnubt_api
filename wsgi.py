from flask import Flask
from ccnubt import login_manager
from config import config
from ccnubt.model import db
from flask_docs import ApiDoc

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

# 本地加载
# app.config['API_DOC_CDN'] = False

# 禁用文档页面
# app.config['API_DOC_ENABLE'] = False

# 需要显示文档的 Api
app.config['API_DOC_MEMBER'] = ['user']

# 需要排除的 RESTful Api 文档
app.config['RESTFUL_API_DOC_EXCLUDE'] = []

ApiDoc(app)


if __name__ == '__main__':

    app.run()
