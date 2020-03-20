from flask import Blueprint
from config.config_flask import config_root

login_blu = Blueprint("login",__name__,url_prefix=config_root + "/login")

from . import view