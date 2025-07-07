# Tripy-Web

## PT0 简介

Tripy-Web 是一个基于 FastAPI 的简单博客与小游戏演示项目，适合课程实验和前后端分离开发入门。
### 开发环境

- Python 3.13.5
- Node.js >= 18.x（当前 v22.17.0）
- npm >= 9.x（当前 v10.9.2）
- 推荐使用 PowerShell 或 Bash 等支持脚本执行的终端


## PT1 启动
### git库克隆
```bash
git clone https://github.com/shxYue/Tripy-Web.git
```
#如果弹出输入用户名和密码的提示，请输入你的 GitHub 用户名和密码（或使用个人访问令牌）。
```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

### 安装依赖

在项目根目录下执行：

```powershell
# 创建并激活虚拟环境
# 临时放开执行策略（如遇到授权失败）
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# 激活新虚拟环境
.\venv\Scripts\activate
# !!一定要确认是开发版本（3.13.5）（python --version）
py -3.13 -m venv venv
#or
python -m venv venv
# Windows PowerShell 下激活
.\venv\Scripts\activate
# Linux/macOS 下激活
source venv/bin/activate

# 使用 requirements.txt 安装所有依赖
pip install -r requirements.txt
#（若网络受限，可加镜像）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

如果想单独安装，也可执行：

```bash
pip install "fastapi[standard]" uvicorn python-jose sqlalchemy "passlib[bcrypt]"
```

### 环境变量配置
在运行服务前，可在根目录创建 `.env` 文件，配置如下：

```properties
# 服务端口
TUNNEL_PORT=8000
# 隧道模式，可选：
#   不设置或空：不启用内网穿透
#   ngrok：使用 ngrok 隧道（需安装 ngrok 并配置 NGROK_AUTH_TOKEN）
#   localtunnel 或 lt：使用 localtunnel 隧道（需全局安装 localtunnel CLI：npm install -g localtunnel）
TUNNEL_MODE=ngrok
# ngrok 授权令牌（可选，ngrok 隧道）
NGROK_AUTH_TOKEN=你的_ngrok_令牌
```

### 启动服务
打开终端，切换到项目根目录
cd d:\pycode\Tripy-Web

# 推荐方式：使用脚本启动，会自动读取 `.env` 端口
```powershell
venv\Scripts\activate
python main.py
```

# 如果仍想使用 uvicorn CLI（需手动指定端口）
```powershell
venv\Scripts\activate
uvicorn main:app --reload --port $Env:TUNNEL_PORT
```

访问接口文档：

http://127.0.0.1:8000/docs

访问前端页面（静态文件）：

http://127.0.0.1:8000/static/pages/index.html
PT2 测试
主页访问：http://127.0.0.1:8000/static/pages/index.html
博客管理：http://127.0.0.1:8000/static/pages/blog_frontend.html
恐龙游戏：http://127.0.0.1:8000/static/pages/dino_game.html
登录/注册：http://127.0.0.1:8000/static/pages/login.html
如有问题请在 issues 区反馈。

### Node.js 安装（如需 localtunnel 内网穿透）
请先安装 Node.js（https://nodejs.org/zh-cn/download/），建议 LTS 版本。
安装完成后，命令行输入 `node -v` 和 `npm -v` 验证。

### 安装 localtunnel CLI
如需使用 localtunnel 内网穿透，需全局安装 localtunnel：
```powershell
npm install -g localtunnel
```
安装完成后，`lt --version` 应能输出版本号。

### requirements.txt 依赖说明
本项目依赖 Python 包见 requirements.txt，已包含 pyngrok、localtunnel（Node.js CLI 需单独 npm 安装）。