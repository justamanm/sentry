#!/usr/bin/env bash

# 注：仅限centos7以上版本

# 安装docker依赖
yum install -y yum-utils device-mapper-persistent-data lvm2

# 配置docker-ce下载源
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

# 安装docker-ce
yum -y install docker-ce

# 启动docker服务，开机自启
systemctl start docker
systemctl enable docker

# 设置镜像源
# 写入源地址到文件daemon.json
cat >> /etc/docker/daemon.json << EOF
{
  "registry-mirrors": [
        "https://registry.cn-hangzhou.aliyuncs.com",		# 阿里镜像加速器，需要注册后获得
        "https://mirror.ccs.tencentyun.com",		# 腾讯云镜像加速器，公开的
        "https://docker.mirrors.ustc.edu.cn",
        "https://registry.docker-cn.com"
  ]
}
EOF

systemctl daemon-reload     # 更新配置
systemctl restart docker	# 重启docker服务

# 安装docker-compose
pip3 install docker-compose