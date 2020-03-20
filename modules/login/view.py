from flask import current_app, request, jsonify, session

from config.config_flask import methods
from modules import handle_log
from . import login_blu


@login_blu.route("/", methods=methods)
def login():
    a = 1/0
    handle_log(msg="-" * 100)

    # 请求是post，所以请求路径中不会有用户信息
    if request.method == "POST":
        data = request.json
        ue = data.get("ue")
        pwd = data.get("pd")
    else:
        ue = request.args.get("ue")
        pwd = request.args.get("pd")

    # ———————————————校验参数—————————————————————
    if not all([ue, pwd]):
        data = {
            'message': 'Bad request',
            'code': 0,
            'exception': '用户名或密码为空',
            'info': ""
        }
        handle_log(msg="登录：参数不足", data=data)
        return jsonify(data)

    # 登录成功
    data = {
        'message': 'Success',
        'code': 1,
        'exception': '',
        'info': ""
    }
    handle_log(msg="登录成功")
    return jsonify(data)
