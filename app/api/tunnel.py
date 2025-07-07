from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import requests as httpx
from app.core.config import TUNNEL_MODE
from app.core.tunnel import last_public_url

router = APIRouter()

@router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def proxy_tunnel(full_path: str, request: Request):
    """代理 localtunnel 请求并注入 bypass header"""
    if TUNNEL_MODE.lower() not in ("localtunnel", "lt"):
        raise HTTPException(status_code=404, detail="Tunnel proxy not enabled")
    public_url = last_public_url
    if not public_url:
        raise HTTPException(status_code=503, detail="Tunnel not available")
    upstream = public_url.rstrip("/") + "/" + full_path
    # 转发 query 和 body
    params = dict(request.query_params)
    body = await request.body()
    # 构建 headers
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    headers["bypass-tunnel-reminder"] = "1"
    headers["User-Agent"] = "MyCustomAgent/1.0"
    # 发起请求
    resp = httpx.request(
        method=request.method,
        url=upstream,
        params=params,
        headers=headers,
        data=body,
        stream=True,
        allow_redirects=False,
    )
    return StreamingResponse(
        resp.raw,
        status_code=resp.status_code,
        headers=dict(resp.headers),
        media_type=resp.headers.get("content-type"),
    )
