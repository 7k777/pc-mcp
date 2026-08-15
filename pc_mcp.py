# -*- coding: utf-8 -*-
"""布丁狗电脑的MCP server v1 - 让林川连上Windows
用法: pip install fastmcp mss uvicorn 然后 python pc_mcp.py
监听: 0.0.0.0:8787 (仅tailnet内网可达)
"""
import subprocess
import os
from datetime import datetime

from fastmcp import FastMCP

try:
    from fastmcp.server.transport import TransportSecuritySettings
except ImportError:
    try:
        from fastmcp.server import TransportSecuritySettings
    except ImportError:
        TransportSecuritySettings = None

mcp = FastMCP("pc-mcp")


@mcp.tool()
def run_command(command: str) -> str:
    """在电脑上执行命令(cmd/PowerShell)，返回输出。命令如: dir, ipconfig, whoami"""
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=90)
        out = (r.stdout or "")[:4000]
        err = (r.stderr or "")[:1500]
        return f"exit={r.returncode}\n{out}\n{err}"
    except Exception as e:
        return f"error: {e}"


@mcp.tool()
def list_dir(path: str = ".") -> str:
    """列出指定目录的内容，默认当前目录"""
    try:
        items = os.listdir(path)
        return "\n".join(items[:300])
    except Exception as e:
        return f"error: {e}"


@mcp.tool()
def read_file(path: str) -> str:
    """读取文本文件内容（前5000字符）"""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()[:5000]
    except Exception as e:
        return f"error: {e}"


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """写入文件（覆盖）。path 用绝对路径，如 D:/test/note.txt"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"written: {path}"
    except Exception as e:
        return f"error: {e}"


@mcp.tool()
def screenshot() -> str:
    """截屏保存到用户目录，返回文件路径"""
    try:
        from mss import mss
        with mss() as sct:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(os.path.expanduser("~"), f"pc_screenshot_{ts}.png")
            sct.shot(output=path)
            return path
    except Exception as e:
        return f"error: {e}"


if __name__ == "__main__":
    import uvicorn
    app = mcp.streamable_http_app(
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=False
        )
    )
    print("pc-mcp 跑起来了，监听 0.0.0.0:8787")
    uvicorn.run(app, host="0.0.0.0", port=8787)
