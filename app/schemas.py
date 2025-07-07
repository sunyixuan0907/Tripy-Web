from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserOut(BaseModel):
    id: int
    username: str
    is_active: bool
    nickname: Optional[str] = None

    class Config:
        from_attributes = True

# 新增：用户更新模型
class UserUpdate(BaseModel):
    nickname: str | None = None
    old_password: str | None = None
    new_password: str | None = None

class BlogCreate(BaseModel):
    title: str
    content: str
    is_public: bool = True  # True=公开，False=私密

class BlogSchema(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: datetime
    is_public: bool
    likes: int = 0
    comments: List["CommentSchema"] = []

    class Config:
        from_attributes = True  # Pydantic V2: 使用 from_attributes 替代 orm_mode

class CommentCreate(BaseModel):
    content: str
    # 评论无需指定作者，直接用当前用户

class CommentSchema(BaseModel):
    id: int
    author: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic V2: 使用 from_attributes 替代 orm_mode

# 添加分数提交和排行榜输出模型
class ScoreSubmit(BaseModel):
    score: int

class LeaderboardEntry(BaseModel):
    username: str
    score: int