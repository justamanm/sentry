from flask import Flask, current_app
from sentry_sdk import capture_exception

from config.config_flask import config_dict, prod_log_level


# 以导包的方式整合sentry
from config import config_sentry


def create_app(model):
    app = Flask(__name__)

    # 配置生产/开发环境下的日志等级
    # 生产模式下：INFO-supervisor+sentry，CRITICAL-sentry
    if model == "prod":
        app.logger.setLevel(prod_log_level)
    else:
        app.logger.setLevel("DEBUG")

    config_class = config_dict[model]
    app.config.from_object(config_class)

    from modules.login import login_blu
    app.register_blueprint(login_blu)

    return app


# 将日志抽为方法，统一在此方法中进行日志记录
# 蓝图中全部调用此方法，不直接使用current_app.logger
def handle_log(e=None, msg=None, data=None):
    if msg:
        current_app.logger.info(msg)
    if data:
        current_app.logger.info(str(data))
    # 要在breadcrumb之后写capture_exception
    capture_exception(e)