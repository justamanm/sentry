###目录

[TOC]



------



### 0.sentry官方博客

- [snuba](https://blog.sentry.io/2019/05/16/introducing-snuba-sentrys-new-search-infrastructure)，storage and search功能的背后(OLAP)
- sentry10，[Self-hosted Sentry 10 is ready to serve - get it while it's hot!](https://blog.sentry.io/2020/01/07/self-hosted-sentry-10-is-ready-to-serve-get-it-while-its-hot)
- [sentry官方论坛](https://forum.sentry.io/c/on-premise/7)



###1.[安装docker](https://www.runoob.com/docker/centos-docker-install.html )

- 卸载旧版本

- 安装依赖：

  ```shell
  yum install -y yum-utils device-mapper-persistent-data lvm2 python3 git
  ```

  - yum-utils 提供了yum-config-manager，用于管理yum仓库

  > yum-utils is a program that can manage main yum configuration options, toggle which repositories are enabled or disabled, and add new repositories.

  - device mapper 存储驱动程序需要 device-mapper-persistent-data 和 lvm2(见[docker存储](#4.docker存储))

    

- 安装Docker Engine-Community(分为社区版和企业版)，先配置下载源

  ```shell
  # 1.设置docker-ce下载源：只能设置一个，重新配置的会覆盖之前的
  # 配置完成后，会保存在：/etc/yum.repos.d/docker-ce.repo
  
  # 官方
  yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
  # 阿里
  yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
  
  # 2.安装docker-ce
  yum -y install docker-ce
  ```

- 启动docker服务&&开机自启，要先启动才会生成/etc/docker目录

  ```shell
  systemctl/service docker start 
  systemctl enable docker		# 开机自启，service没有这个权限，必须用systemcl
  ```

- 配置docker镜像仓库

  - 主要配置阿里云的官方的，之后可以直接拉取自己在阿里云上的镜像

  ```shell
  vi /etc/docker/daemon.json	# 如果没有则创建
  # 填写下面的daemon.json后
  systemctl daemon-reload		# 更新配置 
  systemctl restart docker	# 重启docker服务
  ```

  - [daemon.json](https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors)

  ```yaml
  {
    "registry-mirrors": [
          "https://registry.cn-hangzhou.aliyuncs.com",
          "https://mirror.ccs.tencentyun.com",
          "https://docker.mirrors.ustc.edu.cn",
          "https://registry.docker-cn.com"
    ]
  }
  ```

  参考：[docker下载镜像太慢的解决方案](https://blog.csdn.net/weixin_43569697/article/details/89279225 )

###2.安装Docker-Compose

- [dock三剑客之一](https://www.jianshu.com/p/9634c25955b6)：Compose、Machine、Swarm

- [什么是docker-compose](https://www.runoob.com/docker/docker-compose.html)

  > Docker-Compose项目 是Docker官方的开源项目，负责实现对Docker容器集群的快速编排，是一个用户定义和运行多个容器的 Docker 应用程序。在 Compose 中你可以使用 YAML 文件来配置你的应用服务。然后，只需要一个简单的命令，就可以创建并启动你配置的所有服务。
  >
  > 
  >
  > [docker-compose将所管理的容器分为3层结构](https://blog.csdn.net/qq_35720307/article/details/87256684)：project  service  container
  >
  > docker-compose.yml组成一个project，project里包括多个service，每个service定义了容器运行的镜像（或构建镜像），网络端口，文件挂载，参数，依赖等，每个service可包括同一个镜像的多个容器实例。
  >
  > 即 project 包含 service ，service 包含 container

- 安装

  - 方式1.pip3安装(推荐)

    ```
    pip3 install docker-compose
    ```

  - 方式2.下载安装

    ```liunx
    curl -L https://github.com/docker/compose/releases/download/1.23.0-rc3/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
    
    chmod +x /usr/local/bin/docker-compose
    ```

  - 检查是否安装完成

    - docker-compose version

- [docker-compose.yml的配置及命令](https://blog.csdn.net/qq_35720307/article/details/87256684)

  

### 3.[安装sentry服务端](https://docs.sentry.io/server/installation/)

- 可以通过./install.sh执行安装，也可以手动安装

- ①***自动安装***
  - 获取sentry服务端源码

    ```bash
    git clone https://github.com/justamanm/onpremise.git	# 自定义
    git clone https://github.com/getsentry/onpremise.git	# 官方
    ```
    主目录下的docker-compose.yml，不更改

    ```yaml
    version: '3.4'
    x-restart-policy: &restart_policy
      restart: unless-stopped
    x-sentry-defaults: &sentry_defaults		# 这里即web服务
      << : *restart_policy
      build: # 创建镜像，如果指定build同时也指定image，会从build里构建，镜像的名字和tag将取image指定的
        context: ./sentry	# build时会进入./sentry/目录，执行其中的Dockerfile
        args:
          - SENTRY_IMAGE
      image: sentry-onpremise-local
      depends_on:	# 由于依赖于这些服务，所以会先启动这些服务后building web
        - redis
        - postgres
        - memcached
        - smtp
        - snuba-api
        - snuba-consumer
        - snuba-replacer
        - symbolicator
        - kafka
      environment:
        SNUBA: 'http://snuba-api:1218'
      volumes:
        - 'sentry-data:/data'
    ```

    sentry目录下的Dockerfile，用于build web镜像，不更改

    ```yaml
    ARG SENTRY_IMAGE
    FROM ${SENTRY_IMAGE:-getsentry/sentry:latest}
    
    WORKDIR /usr/src/sentry
    
    # Add WORKDIR to PYTHONPATH so local python files don't need to be installed
    ENV PYTHONPATH /usr/src/sentry
    COPY . /usr/src/sentry
    
    # Hook for installing additional plugins
    RUN if [ -s requirements.txt ]; then pip install -r requirements.txt; fi
    
    # Hook for installing a local app as an addon
    RUN if [ -s setup.py ]; then pip install -e .; fi
    
    # Hook for staging in custom configs
    RUN if [ -s sentry.conf.py ]; then cp sentry.conf.py $SENTRY_CONF/; fi \
            && if [ -s config.yml ]; then cp config.yml $SENTRY_CONF/; fi
    ```

  - 配置环境变量，更改.env

    ```yaml
    COMPOSE_PROJECT_NAME=sentry_onpremise
    SENTRY_EVENT_RETENTION_DAYS=10	# 日志保留时长，手动添加
    SENTRY_IMAGE=aliyun/sentry:getsentry-sentry	# sentry版本，见onpremise的README，手动添加
    ```

  - 问题解决：['module' object has no attribute 'SnubaSearchBackend'](https://forum.sentry.io/t/build-10-1-0-dev0-error-module-object-has-no-attribute-snubasearchbackend/8593)

    ```
    是由于环境变量sentry版本设置不对导致的，git拉取的sentry.conf.py是10版本的，但环境变量写了9.1.2
    配置SENTRY_IMAGE=getsentry/sentry:10后正常
    ```

  - 直接执行./install.sh

    - 如果提示权限不足：chmod 777 install.sh

  - 提升安装完成后执行：docker-compose up -d，开启各服务

  

- ②***手动安装***  (不推荐)

  - 1.生成secret_key：

    - docker-compose run --rm web config generate-secret-key

      - config generate-secret-key：要在容器web内执行的语句

      ```
      多个提示：ERROR: Volume sentry-data declared as external, but could not be found. Please create the volume manually using `docker volume create --name=sentry-data` and try again.
      解决：
      docker volume create --name=sentry-data
      docker volume create --name=sentry-postgres
      docker volume create --name=sentry-redis
      docker volume create --name=sentry-zookeeper
      docker volume create --name=sentry-kafka
      docker volume create --name=sentry-clickhouse
      docker volume create --name=sentry-symbolicator
      
      查看干了什么： 
          find / -name sentry-data
          返回/var/lib/docker/volumes/sentry-data，即创建了sentry-data文件夹
      注：docker的默认存储目录是/var/lib/docker
      ```

    - 执行过程：

      ```
      1.run web时发现没有web服务的镜像，所以在当前目录中的docker-compose.yml中查找web服务配置准备build
      2.由于依赖于redis/memcached/smtp/postgres/zookeeper/kafka/clickhouse/symbolicator/snuba-api服务，而这些服务还并没有对应的镜像，所以全部都pull，之后启动
      3.web服务中的build内容：context：./sentry，即进入sentry目录执行Dockerfile中的命令进行build，
      完成后进入容器执行config generate-secret-key命令，获得secret-key
      ```

  - 2.配置secret-key

    - 将上面得到的secret-key配置到./sentry/config.yml文件的SENTRY_SECRET_KEY项，并取消其注释

    - 在.env文件中添加：

      ```
      SENTRY_SECRET_KEY=*-o_ur-hwc+l*dzd^pwerngf@gmvi3pg&%_)1c=6+4bph@4sov SENTRY_IMAGE=getsentry/sentry:10
      ```

  - 3.配置secret-key后更新

    ```shell
    # 进行web migrate，会启动所依赖的服务
    docker-compose run --rm web upgrade		
    # 如果正常，这一步会要求你填写一个账号密码，用于安装完成之后登录后台的管理员账号，请填写并记录
    ```

  - 4.启动所有服务：

    ```shell
    docker-compose up -d		# 会执行./cron/Dockerfile
    ```

  - 5.TODO [配置](https://docs.sentry.io/server/config/)

    - config.yml
    - sentry.conf.py 

- 重置sentry/docker

  ```
  docker-compose down
  docker-compose rm
  docker volume rm sentry-data sentry-postgres sentry-redis sentry-zookeeper sentry-kafka sentry-clickhouse sentry-symbolicator
  docker rmi getsentry/snuba:latest getsentry/sentry:latest 
  ```

  


#### --------*拓展* 1-基础---------

###4.Dockerfile

- 用于构建docker镜像，在执行docker build时自动读取当前目录下的Dockerfile来构建镜像

- 需要了解构建时所使用的一些命令

  ```
  FROM	基于哪个镜像制作
  WORKDIR	为RUN、CMD、ENTRYPOINT以及COPY和AND设置工作目录
  COPY	复制文件到镜像中
  ADD		也是复制文件到镜像中，但如果是url/压缩包，会自动下载/解压
  RUN		在构建镜像时执行命令，会在FROM获取的镜像上新建一层镜像
  ENTRYPOINT	构建好后在容器中执行的命令，实际执行命令；多个只执行最后一个
  CMD		构建好后在容器中默认执行的命令，通过用于给ENTRYPOINT传参数；多个只执行最后一个
  ENV		为容器指定环境变量
  ARG		接收构建镜像时--build-arg所传的参数，如docker build user=tom(ARP user)，则user为tom
  EXPOSE	声明容器运行的服务端口，相当于-P，宿主机端口随机
  ```

- [教程1-菜鸟教程](https://www.runoob.com/docker/docker-dockerfile.html)，[教程2-你必须知道的Dockerfile](https://www.cnblogs.com/edisonchou/p/dockerfile_inside_introduction.html)
- [CMD和ENTRYPOINT的区别](https://blog.csdn.net/u010900754/article/details/78526443)



### 5.[YAML文件](https://www.runoob.com/w3cnote/yaml-intro.html)

- [介绍](http://www.ruanyifeng.com/blog/2016/07/yaml.html)，文件格式为.yml

- 通过指定的格式来表示结构化的数据，用于编写 配置文件.yml

- 语法规则

  ```
  大小写敏感
  使用缩进表示层级关系
  缩进时不允许使用Tab键，只允许使用空格。
  缩进的空格数目不重要，只要相同层级的元素左侧对齐即可
  # 表示注释
  ```

- 数据结构

  ```
  对象：键值对的集合，又称为映射（mapping）/ 哈希（hashes） / 字典（dictionary）
  数组：一组按次序排列的值，又称为序列（sequence） / 列表（list）
  纯量（scalars）：单个的、不可再分的值
  ```



####--------*拓展* 2-进阶---------

### 6.PostgreSQL

- PostgreSQL 是一个免费的对象-关系数据库服务器 
- PostgreSQL 的Slogan是 "世界上最先进的开源关系型数据库"

### <a id="docker存储">7.docker存储</a>

- [底层技术介绍](https://blog.csdn.net/CSDN_bang/article/details/91917372)

  > Docker 目前支持的驱动类型包括：AUFS、Device mapper、Btrfs、OverlayFS和ZFS(较新) 

- RAID(redundant array of independent disks)：磁盘阵列，由多个磁盘组成一个，读写时所有磁盘同时进行

  - [raid原理技术](https://www.jianshu.com/p/5db387b65d28)

- [Linux内核中的Device Mapper机制](https://www.ibm.com/developerworks/cn/linux/l-devmapper/index.html)

  > Device mapper的用户空间部分对开发者要实现自己的存储管理工具来说是可选的，事实上，很多我们常见的逻辑卷管理器，比如LVM2、dmraid等工具都利用device mapper的提供的device mapper用户空间库，根据自己的管理需求建立独立的一套管理工具，而并没有使用它提供的dmsetup工具，甚至IBM的开源项目企业级的逻辑卷管理系统-EVMS，在实现中都没有采用device mapper的用户空间库，完全根据内核中的ioctl定义实现了一套自己的函数库。 

- [Docker存储驱动之--overlay2](https://www.jianshu.com/p/3826859a6d6e)、[镜像与容器，Overlay2](https://zhuanlan.zhihu.com/p/41958018)

- docker的默认存储目录是/var/lib/docker



###8.Zookeeper

- [zookeeper能做什么](https://blog.csdn.net/java_66666/article/details/81015302)

> zookeeper功能非常强大，可以实现诸如分布式应用配置管理、统一命名服务、状态同步服务、集群管理等功能，我们这里拿比较简单的分布式应用配置管理为例来说明。
>
> 假设我们的程序是分布式部署在多台机器上，如果我们要改变程序的配置文件，需要逐台机器去修改，非常麻烦，现在把这些配置全部放到zookeeper上去，保存在 zookeeper 的某个目录节点中，然后所有相关应用程序对这个目录节点进行监听，一旦配置信息发生变化，每个应用程序就会收到 zookeeper 的通知，然后从 zookeeper 获取新的配置信息应用到系统中。

- kafka基于zookeeper



### 9.kafka

- [kafaka概述](https://blog.csdn.net/sinat_27143551/article/details/93877865)

> kafka是一个分布式消息队列。 同样还有rabbitMQ和redis消息队列。
>
> kafka对外使用topic的概念，生产者往topic里写消息，消费者从读消息。为了做到水平扩展，一个topic实际是由多个partition组成的，遇到瓶颈时，可以通过增加partition的数量来进行横向扩容。单个parition内是保证消息有序。

- [Kafka详细原理总结上](https://www.jianshu.com/p/734cf729d77b )

>Kafka是最初由Linkedin公司开发，是一个分布式、支持分区的（partition）、多副本的（replica），基于zookeeper协调的分布式消息系统，它的最大的特性就是可以实时的处理大量数据以满足各种需求场景：比如基于hadoop的批处理系统、低延迟的实时系统、storm/Spark流式处理引擎，web/nginx日志、访问日志，消息服务等等，用scala语言编写，Linkedin于2010年贡献给了Apache基金会并成为顶级开源 项目。



### 10.ClickHouse

- [ClickHouse概述](https://www.jianshu.com/p/350b59e8ea68)

> 面向列的数据库
>
> ClickHouse是一个面向联机分析处理(OLAP)的开源的面向列式存储的DBMS，简称CK, 与Hadoop, Spark相比，ClickHouse很轻量级,由俄罗斯第一大搜索引擎Yandex于2016年6月发布, 开发语言为C++ 

- [面向列的存储](https://www.jianshu.com/p/43a813e353ce)

  > 与mysql的行存储不同，是在列的方向上存储
  >
  > 原来的字段都是在行方向，现在是在列方向	
  >
  > 如：
  >
  > | 姓名 | 年龄 |  省  | 爱好 |
  > | :--: | :--: | :--: | :--: |
  > | 张三 |  20  |  A   | code |
  >
  > | 张三 | 年龄 |  20  |
  > | :--: | :--: | :--: |
  > | 张三 |  省  |  A   |
  > | 张三 | 爱好 | code |
  >
  > 特点：之前的一条记录无论各字段是否有数据都占用空间，现在没有数据就不需要添加，灵活且节省空间
  >
  > *行式存储相当于套餐，即使一个人来了也给你上八菜一汤，造成浪费；列式存储相等于自助餐，按需自取，人少了也不浪费* 
  >
  > *行式存储更像一个Java Bean，所有字段都提前定义好，且不能改变；列式存储更像一个Map，不提前定义，随意往里添加key/value*



###参考

- [docker使用-菜鸟教程](https://www.runoob.com/docker/docker-hello-world.html )

- [centos7 docker方式部署sentry](https://www.cnblogs.com/watchslowly/p/11309052.html)
- 拓展：[Sentry 高可用部署](https://www.jiankunking.com/sentry-high-availability-deploy.html)