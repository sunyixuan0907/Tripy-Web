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
    # 修改昵称
    if user_update.nickname is not None:
        db_user.nickname = user_update.nickname
    # 修改密码
    if user_update.old_password and user_update.new_password:
        from app.db import pwd_ctx
        if not pwd_ctx.verify(user_update.old_password, db_user.hashed_password):
            raise HTTPException(status_code=400, detail="原密码错误")
        db_user.hashed_password = pwd_ctx.hash(user_update.new_password)
    db.commit()
    db.refresh(db_user)
    return db_user
