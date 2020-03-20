###0.安装
```python
pip3 install sentry-sdk[flask]==0.14.2

注：不能pip3 install sentry，否则会报错：You're trying to run a very old release of Beautiful Soup under Python 3.
```

###1.整合-配置
```python
sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs，只会抓取info及以上等级
    event_level=logging.ERROR  # Send errors as events，error及以上会被当做event而不再是breadcrumb
)

sentry_sdk.init(
    dsn="https://b2fd693327b4451d8d5691a513e1964b@sentry.io/3560845",
    integrations=[FlaskIntegration(), sentry_logging],
    # debug=True,
    request_bodies="never",     # 请求体不会被显示在sentry中
    before_send=before_send,
    before_breadcrumb=before_breadcrumb
)
```

###1.5 分类
- 发送内容分为：event和breadcrumb
- breadcrumb必须依附于event，无法单独发送


###2.两个自定义异常信息方法
- 自定义event和breadcrumbs
- 如果before_send方法中不return，则不会调用before_breadcrumb方法
```python
def before_send(event, hint):
    """
    {'level': 'error', 'exception': {'values': [{'module': 'json.decoder', 'type': 'JSONDecodeError', 'value': 'Extra data: line 1 column
    {'exc_info': (<class 'json.decoder.JSONDecodeError'>,
    :param event:异常事件，包含了异常对象的全部信息
    :param hint:包含3个对象，但不包含异常信息，仅是异常对象而已
    :return:
    """
    print("before_send------------------")
    # 这一句必须没有，否则会导致capture_message生成的event为None，从而不会发送给sentry
    # exc_type, exc_value, tb = hint['exc_info']
    print(event)
    print(hint)
    try:
        # event字典的所有键共14个
        # 必须有event_id，否则sentry收不到异常
        # 如果没有仍然可以收到但会提示的共9个：['level', 'exception', 'modules', 'timestamp', 'request', 'contexts', 'breadcrumbs', 'extra', 'sdk']
        exception = {
            'level': "error",
            'exception': "包含错误栈信息和参数，做处理",
            'event_id': "异常id",
            'timestamp': "时间戳",
            'transaction': "trigger_error，错误触发方式",
            'breadcrumbs': "attach to this even",
            'contexts': "trace等信息(traceid)，runtime信息",
            'modules': "当前项目依赖的python模块",
            'extra': "运行主文件路径",
            'request': "请求信息，url/headers/data等",
            'server_name': "当前主机名，发送请求or服务端所在主机名",
            'sdk': "当前sentry版本、整合信息",
            'platform': "python/java",
            '_meta': "其他信息"
        }
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
        pass
    return event


def before_breadcrumb(crumb, hint):
    """
    {'ty': 'log', 'level': 'info', 'category': 'werkzeug', 'message': '127.0.0.1 - - [06/Mar/2020 13:07:38] "GET /?data=12345. HTTP/1.1
    {'log_record': <LogRecord: werkzeug, 20, C:\Program Files\python_virtual\estate\lib\s
    :param crumb:捕获到的breadcrumbs信息，即app.logger/logging信息
    :param hint:包含3个对象，但不包含异常信息，仅是异常对象而已
    :return:
    """
    print("before_breadcrumb------------------")
    print(crumb)
    print(hint)
    return crumb
```

###3.四个捕获方法
- 3个发送异常event：
    - capture_exception：传入异常对象，适合非自定义，直接发送错误stacktrace信息
        - 如果传入None，在before_send中做处理，不进行发送
    - capture_message：传入异常字符串，适合自定义异常信息
    - capture_event：传入异常字典，适合高度自定义event
- 1个发送breadcrumb，add_breadcrumb
    - 使得不依赖logging而独立对日志等级进行控制
    - 总会发送，而无论level是什么，只有展示图标上的区别
    - 参数：catagory/message/data/level/type
    - level参数：fatal, error, warning, info, debug
    - type参数：default，http，error，由于default图标一致，所以选择
- 由于capture_event传入字典很便捷，所以选择

###4.异常信息的发送控制
- 如果用add_breadcrumb，则sentry与flask日志控制完全分离
- 如果使用app.logger，则无法做到分离
    - flask中日志是否记录取决于app.logger.setLevel()的设置
    - sentry日志等级由flask和sentry共同决定，等级取二者最高的

###5.注意点
- before_send方法中不能有hint["exc_info"]，否则会导致event为None，不会发送event

