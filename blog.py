from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_blogs():
    return [{"id": 1, "title": "test"}]

app = FastAPI()

# 博客数据模型
class Blog(BaseModel):
    id: int
    title: str
    content: str
    author: Optional[str] = None

# 内存数据库
blogs: List[Blog] = []

# 创建博客
@app.post("/blogs/", response_model=Blog)
def create_blog(blog: Blog):
    for b in blogs:
        if b.id == blog.id:
            raise HTTPException(status_code=400, detail="ID already exists")
    blogs.append(blog)
    return blog

# 获取所有博客
@app.get("/blogs/", response_model=List[Blog])
def read_blogs():
    return blogs

# 获取单个博客
@app.get("/blogs/{blog_id}", response_model=Blog)
def read_blog(blog_id: int):
    for blog in blogs:
        if blog.id == blog_id:
            return blog
    raise HTTPException(status_code=404, detail="Blog not found")

# 更新博客
@app.put("/blogs/{blog_id}", response_model=Blog)
def update_blog(blog_id: int, new_blog: Blog):
    for idx, blog in enumerate(blogs):
        if blog.id == blog_id:
            blogs[idx] = new_blog
            return new_blog
    raise HTTPException(status_code=404, detail="Blog not found")

# 删除博客
@app.delete("/blogs/{blog_id}")
def delete_blog(blog_id: int):
    for idx, blog in enumerate(blogs):
        if blog.id == blog_id:
            blogs.pop(idx)
            return {"detail": "Blog deleted"}
    raise HTTPException(status_code=404, detail="Blog not found")
