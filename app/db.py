from typing import List, Optional
from app.schemas import BlogSchema, CommentSchema   # 将 Pydantic 模型 BlogSchema 当作 Blog 引入
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .models import User
from datetime import datetime

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str) -> User:
    user = User(
        username=username,
        hashed_password=pwd_ctx.hash(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

class BlogStore:
    def get_all(self) -> List[BlogSchema]:
        raise NotImplementedError()

    def create_blog(self, blog: BlogSchema) -> BlogSchema:
        raise NotImplementedError()

    def get_blog(self, blog_id: int) -> Optional[BlogSchema]:
        raise NotImplementedError()

    def update_blog(self, blog_id: int, new_blog: BlogSchema) -> BlogSchema:
        raise NotImplementedError()

    def delete_blog(self, blog_id: int) -> None:
        raise NotImplementedError()


class MemoryBlogStore(BlogStore):
    def __init__(self):
        self.blogs: List[BlogSchema] = []
        self.next_comment_id = {}  # 存储每个 blog 的下一个 comment id
        self.like_map: dict[int, set[str]] = {}  # 存储每个 blog 被哪些用户点赞

    def get_all(self) -> List[BlogSchema]:
        return self.blogs

    def create_blog(self, blog: BlogSchema) -> BlogSchema:
        if any(b.id == blog.id for b in self.blogs):
            raise Exception("Blog with this id already exists")
        # 初始化 likes、comments、like_map
        blog.likes = 0
        blog.comments = []
        self.next_comment_id[blog.id] = 1
        self.like_map[blog.id] = set()
        self.blogs.append(blog)
        return blog

    def get_blog(self, blog_id: int) -> Optional[BlogSchema]:
        for blog in self.blogs:
            if blog.id == blog_id:
                return blog
        return None

    def update_blog(self, blog_id: int, new_blog: BlogSchema) -> BlogSchema:
        for idx, blog in enumerate(self.blogs):
            if blog.id == blog_id:
                self.blogs[idx] = new_blog
                return new_blog
        raise Exception("Blog not found")

    def delete_blog(self, blog_id: int) -> None:
        for idx, blog in enumerate(self.blogs):
            if blog.id == blog_id:
                self.next_comment_id.pop(blog_id, None)
                self.like_map.pop(blog_id, None)
                self.blogs.pop(idx)
                return
        raise Exception("Blog not found")
    
    # 新增：点赞/取消点赞功能，每个用户可切换点赞状态
    def like_blog(self, blog_id: int, username: str) -> int:
        blog = self.get_blog(blog_id)
        if not blog:
            raise Exception("Blog not found")
        users = self.like_map.get(blog_id)
        if username in users:
            users.remove(username)
        else:
            users.add(username)
        blog.likes = len(users)
        return blog.likes
    
    # 新增：添加评论
    def add_comment(self, blog_id: int, author: str, content: str) -> CommentSchema:
        blog = self.get_blog(blog_id)
        if not blog:
            raise Exception("Blog not found")
        cid = self.next_comment_id.get(blog_id, 1)
        comment = CommentSchema(id=cid, author=author, content=content, created_at=datetime.utcnow())
        blog.comments.append(comment)
        self.next_comment_id[blog_id] = cid + 1
        return comment
    
    # 新增：获取评论列表
    def get_comments(self, blog_id: int) -> List[CommentSchema]:
        blog = self.get_blog(blog_id)
        if not blog:
            raise Exception("Blog not found")
        return blog.comments


# 默认使用内存实现
blog_store = MemoryBlogStore()