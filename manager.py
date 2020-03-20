import os
import sys

# 配置模块查找路径，在环境变量中添加根路径
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path)

from modules import create_app
from config.config_flask import pattern

# "dev": DevConfig；"prod": ProdConfig；日志的level：dev-DEBUG,prod-CRITICAL
app = create_app(pattern)

# from flask.helpers import get_env
# print(get_env())  # 获取当前环境变量FLASK_ENV

if __name__ == '__main__':
    app.run("0.0.0.0", 5000)




