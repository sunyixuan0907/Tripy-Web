import os
from dotenv import load_dotenv
import subprocess  # 新增：用于静默子进程输出

# 1. 启动前先删除数据库文件
db_path = os.path.join(os.path.dirname(__file__), "app", "data.db")
if os.path.exists(db_path):
    os.remove(db_path)

load_dotenv()  # 加载根目录 .env 文件中的配置
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import blog, auth, dino_game, admin
from fastapi.staticfiles import StaticFiles
from pyngrok import ngrok, conf
from app.core.config import NGROK_AUTH_TOKEN
from app.core.database import Base, engine
from fastapi.responses import RedirectResponse

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

@app.get("/", include_in_schema=False)
def root():
    # 根路由重定向到前端首页
    return RedirectResponse(url="/static/pages/index.html")

@app.on_event("startup")
def on_startup():
    print("Debug: NGROK_AUTH_TOKEN:", repr(NGROK_AUTH_TOKEN))
    try:
        # 终止已有 ngrok 会话
        try:
            ngrok.kill()
        except Exception:
            pass
        # 配置 ngrok 日志级别和禁止 Web 界面，降低终端噪音
        default_conf = conf.get_default()
        default_conf.auth_token = NGROK_AUTH_TOKEN
        default_conf.log_level = "ERROR"
        default_conf.web_addr = False
        # 启动 ngrok 隧道，静默子进程输出
        public_url = ngrok.connect(
            8000,
            subprocess_kwargs={"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        ).public_url
        print(f"🔗 Public URL: {public_url}")
    except Exception as e:
        print("❌ ngrok 隧道启动失败：", e)

# 2. 再创建表
Base.metadata.create_all(bind=engine)