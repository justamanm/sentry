
# ---------------------------配置类，工厂模式---------------------------
class Config:
    SECRET_KEY = "xxx"
    JSON_AS_ASCII = False


class DevConfig(Config):
    DEBUG = True
    ENV = "development"


class ProdConfig(Config):
    DEBUG = False
    ENV = "production"


config_dict = {
    "dev": DevConfig,
    "prod": ProdConfig
}

# ---------------------------配置开发环境(dev)/生产环境(prod)---------------------------
pattern = "dev"

# ---------------------------配置请求方法---------------------------
if pattern == "dev":
    methods = ["POST", "GET"]
else:
    methods = ["POST", "GET"]

# ---------------------------配置路由根路径---------------------------
config_root = "/app"

# ---------------------------配置日志记录等级，仅sentry或(sentry+supervisor)---------------------------
prod_log_level = "INFO"     # INFO-同时记录 WARNING-同时但对supervisor做限制 CRITICAL-仅sentry

