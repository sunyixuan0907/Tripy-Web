from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List

router = APIRouter()

# --------- 数据模型 ---------
class SurfGame(BaseModel):
    player: str
    position: int = 0
    score: int = 0
    is_active: bool = False

class SubmitScore(BaseModel):
    player: str
    score: int

class LeaderboardEntry(BaseModel):
    player: str
    score: int

# --------- 内存存储 ---------
surf_games: Dict[str, SurfGame] = {}
leaderboard: List[LeaderboardEntry] = []

# --------- 游戏 API ---------
@router.post("/start", response_model=SurfGame, summary="开始游戏")
def start_game(player: str):
    game = SurfGame(player=player, is_active=True)
    surf_games[player] = game
    return game

@router.post("/forward", response_model=SurfGame, summary="前进一步")
def surf_forward(player: str):
    game = surf_games.get(player)
    if not game or not game.is_active:
        raise HTTPException(status_code=400, detail="请先开始游戏")
    game.position += 1
    game.score += 10
    return game

@router.get("/status", response_model=SurfGame, summary="获取游戏状态")
def surf_status(player: str):
    game = surf_games.get(player)
    if not game:
        raise HTTPException(status_code=404, detail="没有找到该玩家的游戏")
    return game

@router.post("/reset", response_model=SurfGame, summary="重置游戏")
def surf_reset(player: str):
    if player not in surf_games:
        raise HTTPException(status_code=404, detail="没有找到该玩家的游戏")
    game = SurfGame(player=player)
    surf_games[player] = game
    return game

# --------- 排行榜 API ---------
@router.post("/submit", response_model=List[LeaderboardEntry], summary="提交分数")
def submit_score(item: SubmitScore):
    # 添加并保持排行榜前 10
    entry = LeaderboardEntry(**item.dict())
    leaderboard.append(entry)
    leaderboard.sort(key=lambda e: e.score, reverse=True)
    return leaderboard[:10]

@router.get("/leaderboard", response_model=List[LeaderboardEntry], summary="获取排行榜")
def get_leaderboard():
    return leaderboard[:10]