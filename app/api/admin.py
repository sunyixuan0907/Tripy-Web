from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.database import SessionLocal
from app.models import User
from app.schemas import UserOut
from app.api.auth import get_current_user

router = APIRouter(tags=["admin"])

ADMIN_USERNAME = "admin"      # 这里修改管理员账号
ADMIN_PASSWORD = "admin123"   # 这里修改管理员密码

class AdminLoginIn(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def admin_login(data: AdminLoginIn):
    if data.username == ADMIN_USERNAME and data.password == ADMIN_PASSWORD:
        return {"msg": "ok", "token": "admin-token"}
    raise HTTPException(401, "用户名或密码错误")

@router.get("/users", response_model=List[UserOut], summary="获取所有用户（仅 admin）")
def list_users(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("X-Admin-Token")
    if token != "admin-token":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="无权限")
    return db.query(User).all()