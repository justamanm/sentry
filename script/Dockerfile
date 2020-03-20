# 用于根据centos7创建项目镜像，仅在构建镜像时使用
# docker build --rm -t xxx -f ./script/Dockerfile .

FROM centos:7

# 指定容器的工作目录
WORKDIR /home/python/code/sentry
COPY . .

# 安装python3和离线模块
RUN yum install -y python3 && cd packages_linux && pip3 install --no-index --find-links=. -r requirements.txt && cd .. && rm -rf * && cd ..

# 配置使得系统支持中文
RUN yum install -y kde-l10n-Chinese && yum install -y glibc-common && localedef -c -f UTF-8 -i zh_CN zh_CN.utf8 && echo "export LANG=zh_CN.UTF-8" >> /etc/locale.conf
ENV LC_ALL=zh_CN.UTF-8 LANG=zh_CN.UTF-8 TZ=Asia/Shanghai

# 如果用build创建，则把注释打开
# 进入容器后执行的命令，启动supervisor
#ENTRYPOINT ["/bin/bash", "-c", "supervisord -c /home/python/code/sentry/supervisor/supervisord.conf"]
