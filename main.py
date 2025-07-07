import os
import subprocess  # 用于静默子进程输出
import logging
import requests  # 用于获取已存在隧道
from dotenv import load_dotenv
# 加载 .env 配置，override=True 确保 .env 变量每次覆盖
load_dotenv(override=True)

import asyncio
try:
    from asyncio import WindowsSelectorEventLoopPolicy
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
except ImportError:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from app.core.config import NGROK_AUTH_TOKEN, TUNNEL_PORT, TUNNEL_MODE
from app.core.tunnel import setup_tunnel
from app.core.database import Base, engine

from app.api import blog, auth, dino_game, admin, user
from app.api.tunnel import router as tunnel_router  # localtunnel 代理
from app.core.config import TUNNEL_MODE  # 隧道模式

# 屏蔽 pyngrok 和二进制日志输出
logging.getLogger("pyngrok").setLevel(logging.ERROR)
logging.getLogger("pyngrok.ngrok").setLevel(logging.ERROR)

PUBLIC_URL: str = ""  # 存储隧道地址

# Lifespan manager for tunnels
@asynccontextmanager
async def lifespan(app: FastAPI):
    public_url, _ = setup_tunnel(TUNNEL_PORT)
    if public_url:
        print(f"🔗 公网 URL: {public_url}")
    yield

# 仅在启用隧道模式时使用 lifespan
if TUNNEL_MODE.lower() in ("ngrok", "localtunnel", "lt"):
    app = FastAPI(lifespan=lifespan)
else:
    app = FastAPI()

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(blog.router, prefix="/blogs")
app.include_router(auth.router, prefix="/auth")
app.include_router(dino_game.router, prefix="/dino")
app.include_router(admin.router, prefix="/admin")
app.include_router(user.router, prefix="/users")  # 注册用户管理路由
if TUNNEL_MODE.lower() in ("localtunnel", "lt"):
    app.include_router(tunnel_router, prefix="/tunnel", tags=["tunnel"])  # 代理 localtunnel 请求

@app.get("/", include_in_schema=False)
def root():
    # 根路由重定向到前端首页
    return RedirectResponse(url="/static/pages/index.html")

# 删除旧数据库文件，确保表结构与模型同步（会清空所有数据）
db_path = os.path.join(os.path.dirname(__file__), "app", "data.db")
if os.path.exists(db_path):
    os.remove(db_path)

# 2. 再创建表
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    # 直接用 Python 运行时，自动启动隧道并启动服务
    # 自动发起隧道
    public_url, _ = setup_tunnel(TUNNEL_PORT)
    if public_url:
        print(f"🔗 公网 URL: {public_url}")
    else:
        print("❌ 未启用或无法获取隧道 URL")
    # 启动 FastAPI 服务
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=TUNNEL_PORT)