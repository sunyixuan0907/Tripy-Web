from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'data.db'}"
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN", "")
TUNNEL_PORT = int(os.getenv("TUNNEL_PORT", "8000"))
TUNNEL_MODE = os.getenv("TUNNEL_MODE", "")  # 隧道模式: 'ngrok', 'localtunnel' (或 'lt')，或空表示不启用
LOCALTUNNEL_SUBDOMAIN = os.getenv("LOCALTUNNEL_SUBDOMAIN", "")  # localtunnel 子域名，留空则随机