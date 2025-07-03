from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import UserOut, UserUpdate
from app.api.auth import get_current_user, get_db
from app.models import User

router = APIRouter(tags=["user"])

@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@router.patch("/me", response_model=UserOut)
def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新当前用户昵称"""
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db_user.nickname = user_update.nickname
    db.commit()
    db.refresh(db_user)
    return db_user
