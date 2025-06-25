# Tripy-Web

PT0 简介

Test items for the course

代码基于python 3.13.5 fastapi 0.115.13 unicorn 0.34.3

运行前需要安装fastapi&uvicorn 

PT1 服务支持

安装fastapi：终端：pip install "fastapi[standard]"

安装uvicorn：终端：pip install uvicorn

运行时先将终端定位到代码所在位置：使用命令：cd:\code\.vscode  #注意是你的电脑的代码所在文件夹路径

启动服务：uvicorn blog:app --reload

PT2 测试

代码测试软件postman

在 Postman 中调用 FastAPI 的接口时，常用如下选项：

GET（获取所有博客）选择 GET 方法 URL: http://127.0.0.1:8000/blogs/  ##详细格式见blog.py
