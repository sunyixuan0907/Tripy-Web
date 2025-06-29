from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import blog, auth, dino_game
from fastapi.staticfiles import StaticFiles

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