import json
from flask import Flask
import logging
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


def before_send(event, hint):
    """
    event:{'level': 'error', 'exception': {'values': [{'module': 'json.decoder', 'type': 'JSONDecodeError', 'value': 'Extra data: line 1 column
    hint:{'exc_info': (<class 'ZeroDivisionError'>, ZeroDivisionError('division by zero',), <traceback object at 0x000002627CCFCC48>)}
    注：必须没有hint['exc_info']的操作，否则会导致capture_message生成的event为None，从而不会发送给sentry
    :param event:异常事件，包含了异常对象的全部信息
    :param hint:包含3个对象，但不包含异常信息，仅是异常对象而已
    :return:
    """

    # event字典的所有键共14个
    # 必须有event_id，否则sentry收不到异常
    # 如果没有仍然可以收到但会提示的共9个：['level', 'exception', 'modules', 'timestamp', 'request', 'contexts', 'breadcrumbs', 'extra', 'sdk']
    # exception = {
    #     'level': "error",
    #     'exception': "包含错误栈信息和参数，做处理",
    #     'event_id': "异常id",
    #     'timestamp': "时间戳",
    #     'transaction': "trigger_error，错误触发方式",
    #     'breadcrumbs': "attach to this even",
    #     'contexts': "trace等信息(traceid)，runtime信息",
    #     'modules': "当前项目依赖的python模块",
    #     'extra': "运行主文件路径",
    #     'request': "请求信息，url/headers/data等",
    #     'server_name': "当前主机名，发送请求or服务端所在主机名",
    #     'sdk': "当前sentry版本、整合信息",
    #     'platform': "python/java",
    #     '_meta': "其他信息"
    # }

    # 如果删减event过程中出错则丢弃
    try:
        # 处理capture_exception(None)
        # event["exception"]["values"]为列表类型
        # 如果传None，event["exception"]["values"]为[]，丢掉event
        if not event["exception"]["values"]:
            return

        # 控制是否要处理错误信息
        status = True
        if status:
            for key, value in event.items():
                if key == "exception":
                    values_list = event["exception"]["values"]
                    for value in values_list:
                        stacktrace_list = value["stacktrace"]["frames"]
                        for stacktrace in stacktrace_list:
                            stacktrace["vars"] = ""
                elif key in ["message", "level", "event_id", "timestamp", "transaction", "breadcrumbs"]:
                    pass
                else:
                    event[key] = ""
    except:
        return
    return event


def before_breadcrumb(crumb, hint):
    """
    {'ty': 'log', 'level': 'info', 'category': 'werkzeug', 'message': '127.0.0.1 - - [06/Mar/2020 13:07:38] "GET /?data=12345. HTTP/1.1
    {'log_record': <LogRecord: werkzeug, 20, C:\Program Files\python_virtual\estate\lib\s
    :param crumb:捕获到的breadcrumbs信息，即app.logger/logging信息
    :param hint:包含3个对象，但不包含异常信息，仅是异常对象而已
    :return:
    """
    # print("before_breadcrumb------------------")
    # print(crumb)
    # print(hint)
    # if 'log_record' in hint:
    #     crumb['data']['thread'] = hint['log_record'].threadName
    return crumb


sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)

sentry_sdk.init(
    # dsn="https://xxxxxxxxxxxxxxxxxxxxxxx@sentry.io/3560845",     # sentry官方
    # dsn="http://xxxxxxxxxxxxxxxxxxx@134.175.151.196:9000/1",     # 本地sentry服务器
    dsn="http://xxxxxxxxxxxxxxxxxxxx@47.98.239.206:9000/2",     # 阿里云sentry服务器
    integrations=[FlaskIntegration(), sentry_logging],
    # debug=True,
    request_bodies="never",     # 请求体不会被显示在sentry中
    before_send=before_send,
    before_breadcrumb=before_breadcrumb
)