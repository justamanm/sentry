#!/usr/bin/env bash

# 注：命令不能用变量，否则不会执行
volume_path="/home/python/code/sentry"
# 默认运行本地的项目镜像：local/sentry:1.0
image_name="local/sentry:1.0"

# docker-hub镜像仓库
#docker pull xxx
#image_name="xxx"

# 阿里云仓库
#docker pull yyy
#image_name="yyy"
#docker pull registry.cn-hangzhou.aliyuncs.com/yyy

# 启动容器
docker run -itd -v $volume_path:$volume_path -p 5000:5000 --name sentry_container $image_name /bin/bash -c "supervisord -c /home/python/code/sentry/supervisor/supervisord.conf && top -c"
