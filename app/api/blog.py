from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import BlogSchema, BlogCreate, CommentCreate, CommentSchema
from typing import List
from datetime import datetime
from app.api.auth import get_current_user
from app.db import BlogStore, MemoryBlogStore
from app.models import User

router = APIRouter(tags=["blogs"])

# 按用户名分隔存储
user_blogs: dict[str, MemoryBlogStore] = {}

def get_store(user: User) -> MemoryBlogStore:
    return user_blogs.setdefault(user.username, MemoryBlogStore())

# helper: 根据 blog_id 查找对应用户的 store
def find_store_and_owner(blog_id: int):
    for username, store in user_blogs.items():
        if store.get_blog(blog_id):
            return username, store
    return None, None

@router.get("/", response_model=List[BlogSchema], summary="获取所有博客")
def read_blogs(current_user: User = Depends(get_current_user)):
    # 公开博客对所有用户可见，私密博客仅作者可见
    all_blogs: List[BlogSchema] = []
    for username, store in user_blogs.items():
        for b in store.get_all():
            if b.is_public or username == current_user.username:
                all_blogs.append(b)
    # 按发布时间倒序
    return sorted(all_blogs, key=lambda x: x.created_at, reverse=True)

@router.post("/", response_model=BlogSchema, status_code=201, summary="创建博客")
def create_blog(blog: BlogCreate, current_user: User = Depends(get_current_user)):
    store = get_store(current_user)
    # 自动生成连续 ID
    existing = store.get_all()
    next_id = max((b.id for b in existing), default=0) + 1
    new_blog = BlogSchema(
        id=next_id,
        title=blog.title,
        content=blog.content,
        author=current_user.username,
        created_at=datetime.utcnow(),
        is_public=blog.is_public
    )
    return store.create_blog(new_blog)

@router.get("/{blog_id}", response_model=BlogSchema, summary="获取单个博客")
def read_blog(blog_id: int, current_user: User = Depends(get_current_user)):
    b = get_store(current_user).get_blog(blog_id)
    if not b:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    return b

@router.put("/{blog_id}", response_model=BlogSchema, summary="更新博客")
def update_blog(blog_id: int, new_blog: BlogCreate, current_user: User = Depends(get_current_user)):
    store = get_store(current_user)
    existing = store.get_blog(blog_id)
    if not existing:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    # 生成更新的 BlogSchema，保留 author 和 created_at，并更新公开状态
    updated = BlogSchema(
        id=blog_id,
        title=new_blog.title,
        content=new_blog.content,
        author=current_user.username,
        created_at=existing.created_at,
        is_public=new_blog.is_public
    )
    return store.update_blog(blog_id, updated)

@router.delete("/{blog_id}", status_code=204, summary="删除博客")
def delete_blog(blog_id: int, current_user: User = Depends(get_current_user)):
    store = get_store(current_user)
    if not store.get_blog(blog_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    store.delete_blog(blog_id)
    # 返回 204 时不需要 Body

# 点赞博客
@router.post("/{blog_id}/like", summary="点赞博客")
def like_blog(blog_id: int, current_user: User = Depends(get_current_user)):
    owner, store = find_store_and_owner(blog_id)
    if not store:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    blog = store.get_blog(blog_id)
    if not blog.is_public and owner != current_user.username:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "无权限")
    try:
        likes = store.like_blog(blog_id, current_user.username)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return {"likes": likes}

# 添加评论
@router.post("/{blog_id}/comments", response_model=CommentSchema, summary="添加评论")
def add_comment(blog_id: int, comment: CommentCreate, current_user: User = Depends(get_current_user)):
    owner, store = find_store_and_owner(blog_id)
    if not store:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    blog = store.get_blog(blog_id)
    if not blog.is_public and owner != current_user.username:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "无权限")
    return store.add_comment(blog_id, current_user.username, comment.content)

# 获取评论列表
@router.get("/{blog_id}/comments", response_model=List[CommentSchema], summary="获取评论")
def get_comments(blog_id: int, current_user: User = Depends(get_current_user)):
    owner, store = find_store_and_owner(blog_id)
    if not store:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    blog = store.get_blog(blog_id)
    if not blog.is_public and owner != current_user.username:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "无权限")
    return store.get_comments(blog_id)