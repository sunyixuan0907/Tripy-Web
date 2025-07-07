import subprocess
import logging
import re
from pyngrok import ngrok
from pyngrok.conf import PyngrokConfig
import os
from .config import NGROK_AUTH_TOKEN, LOCALTUNNEL_SUBDOMAIN

# 屏蔽 pyngrok 日志
logging.getLogger("pyngrok").setLevel(logging.ERROR)
logging.getLogger("pyngrok.ngrok").setLevel(logging.ERROR)

last_public_url = None  # 存储最近一次获取的隧道 URL


def get_existing_ngrok_tunnel_url(port: int):
    """通过 ngrok 本地 API 获取已存在隧道的公网 URL"""
    try:
        resp = subprocess.check_output(["curl", "-s", "http://127.0.0.1:4040/api/tunnels"]).decode()
        data = __import__('json').loads(resp)
        for t in data.get("tunnels", []):
            if f"{port}" in t.get("config", {}).get("addr", ""):
                return t.get("public_url")
    except Exception:
        return None
    return None


def start_ngrok(port: int):
    """启动 ngrok 隧道"""
    try:
        ngrok.kill()
    except Exception:
        pass
    if NGROK_AUTH_TOKEN:
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
    config = PyngrokConfig(auth_token=NGROK_AUTH_TOKEN, web_addr=False, no_log=True,
                           subprocess_kwargs={"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL})
    tunnel = ngrok.connect(port, pyngrok_config=config)
    return tunnel.public_url


def start_localtunnel(port: int):
    """启动 localtunnel 隧道，首选 lt，其次 npx localtunnel，使用 DETACHED_PROCESS 后台运行"""
    from shutil import which
    # 准备环境变量，加入 npm bin
    env = os.environ.copy()
    appdata = os.getenv('APPDATA')
    if appdata:
        npm_bin = os.path.join(appdata, 'npm')
        env['PATH'] = npm_bin + os.pathsep + env.get('PATH', '')

    # 选择命令
    if which('lt'):
        base_cmd = 'lt'
    elif which('npx'):
        base_cmd = 'npx localtunnel'
    else:
        print('[tunnel] 未找到 lt 或 npx，可全局安装 localtunnel CLI')
        return None

    cmd = f"{base_cmd} --port {port}"
    if LOCALTUNNEL_SUBDOMAIN:
        cmd += f" --subdomain {LOCALTUNNEL_SUBDOMAIN}"
    print(f"[tunnel] 执行: {cmd} (超时 60s)")
    try:
        # 同步获取首行 URL，超时 60 秒
        completed = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, env=env, timeout=60
        )
        out = completed.stdout + completed.stderr
        for line in out.splitlines():
            print(f"[tunnel] 输出: {line}")
            m = re.search(r"https://\S+", line)
            if m:
                url = m.group(0)
                # 后台启动持久进程
                flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
                subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
                    env=env, creationflags=flags
                )
                return url
        print('[tunnel] 未检测到 URL，localtunnel 启动可能失败')
    except subprocess.TimeoutExpired:
        print('[tunnel] localtunnel 启动超时')
    except Exception as e:
        print(f"[tunnel] 执行失败: {e}")
    return None


def setup_tunnel(port: int):
    """根据环境变量选择隧道模式，返回公网 URL"""
    mode = os.getenv("TUNNEL_MODE", "").lower()
    public_url = None
    if mode == 'ngrok':
        try:
            public_url = start_ngrok(port)
        except Exception:
            public_url = get_existing_ngrok_tunnel_url(port)
    elif mode in ('localtunnel', 'lt'):
        # Localtunnel 模式下不自动启动，请手动在终端运行 lt --port
        print(f"[tunnel] Localtunnel 模式，请手动运行: lt --port {port}")
        return None, None
    else:
        # 未启用隧道或未知模式
        return None, None

    # 记录 URL
    global last_public_url
    last_public_url = public_url
    return public_url, None
