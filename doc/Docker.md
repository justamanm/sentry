##制作项目本地镜像
####1.编写Dockerfile
- 用于创建某个服务的镜像
- 具体：
    - 基于centos:7镜像
    - 将项目目录拷贝到虚拟机相应目录，用于安装离线包，安装完成后删除文件，保证在镜像中没有代码存在
    - 安装依赖：
        - python3/离线模块
        - 使系统支持中文：kde-l10n-Chinese/glibc-common，localedef命令，配置环境变量
- docker-compose
    - 用于管理多个服务
- 部署时，两者都可以实现

####2.两种生成镜像的方式
- build命令
    - 默认使用当前目录的Dockerfile，只生成镜像
    ```bash
    docker build -t runoob/ubuntu:v1 .
    docker build -f /path/to/a/Dockerfile . 
    ```
    - 后面的点指明将哪个文件夹传给docker daemon进行构建
    
- docker-compose
    - 在其中指定Dockerfile目录
    - 除了调用Dockfile创建镜像，还会自动生成并启动容器
        - 可以在其中指定启动容器时的命令/端口/挂载卷等，与run相同
    
##远程镜像仓库    
####1.上传镜像
- 首先在两个平台创建个人仓库：阿里云或Docker Hub
- 会产生镜像地址，其构成：域名+命名空间+仓库名:标签
    - 在/etc/docker/daemon.json中写的就是域名
    - 阿里云：https://registry.cn-hangzhou.aliyuncs.com
    - Docker Hub：https://registry.docker-cn.com
    - 域名配置好后，将自己的仓库设置为公开，就可以通过FROM/images搜索到从而自动拉取
- 阿里云
    ```bash
    # 登录，然后输入密码即可
    docker login --username=[登录用户名] registry.cn-hangzhou.aliyuncs.com
    # 打标签
    docker tag [ImageId] registry.cn-hangzhou.aliyuncs.com/dockers-repo/[阿里仓库名]:[标签名]
    # 推送；(如果本身用的就是云服务器，则可以用内网地址推送，速度快)
    docker push registry.cn-hangzhou.aliyuncs.com/dockers-repo/[阿里仓库名]:[上面配置的标签名]
    ```
- Docker Hub
    ```bash
    # 登录，然后输入密码即可
    docker login
    # 打标签，注：标签名要加上hub仓库前缀和冒号，如[docker用户名]/[仓库地址]:latest
    docker tag [ImageId] [标签名]
    # 推送
    docker push [上面配置的带仓库前缀的tag]
    ```
####2.拉取镜像
- 阿里云
    ```bash
    docker pull registry.cn-hangzhou.aliyuncs.com/dockers-repo/[阿里仓库名]:[标签名]
    ```
- Docker Hub
    ```bash
    docker pull [用户名-命名空间]/[仓库名]:[tagname]
    ```

##两种方式获取并部署项目镜像
####1.脚本部署:run_docker.sh
- pull拉取远程仓库的项目镜像
- run运行容器
- 之后通过docker命令管理
####2.docker-compose部署
- images指定远程仓库的项目镜像
- ports/volumes/container_name/command等指定容器运行情况
- 之后可以通过docker和docker-compose命令管理

### 文件说明
- install_docker.sh
    - 安装docker和docker-compose
    - docker开机自启
    - 配置镜像源，docker-compose.yml里的images和Dockefile里的FROM会用到
    