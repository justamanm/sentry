##部署流程


###使用docker部署
- 特点：
    - 不依赖于部署环境，只要支持docker即可
    - 部署简单，方便
- 具体有两种方式：
    - 1.通过脚本运行项目
        ```
        sh run_docker.sh
        ```
    - 2.通过docker-compose运行项目
        ```
        docker-compose up -d
    - 两种方式一致，选择其一即可，具体参考Docker.md
  

## 文件说明

- manager.py：主程序启动文件
- doc/：说明性文件夹
- log/：日志文件夹，主要是supervisor_stderr中的内容
- modules/：各个蓝图
- packages_linux/：离线安装模块文件夹
- utils/：工具类，开发使用

- supervisor说明：
    - supervisor/：配置文件夹，包含supervisor及其子应用的配置
    - supervisord：配置supervisord为服务的脚本  
    - doc/supervisor配置说明.txt：提取出需要配置那些内容
    - doc/start_supervisor.sh：手动启动supervisor脚本



