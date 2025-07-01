import os

# 1. 启动前先删除数据库文件
db_path = os.path.join(os.path.dirname(__file__), "app", "data.db")
if os.path.exists(db_path):
    os.remove(db_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import blog, auth, dino_game, admin
from fastapi.staticfiles import StaticFiles
from app.core.database import Base, engine

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

# 2. 再创建表
Base.metadata.create_all(bind=engine)