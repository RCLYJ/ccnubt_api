# coding: utf-8
from flask import  Blueprint

bp = Blueprint('user', __name__, url_prefix='/user')

from . import user0
from . import user1