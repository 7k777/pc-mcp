# -*- coding: utf-8 -*-
"""pc-mcp v2: 纯标准库零依赖版 - 布丁狗电脑的MCP server
用法: python pc_mcp.py  (任何Python版本，不需要装任何包)
监听: 0.0.0.0:8787 (仅tailnet内网可达)
"""
import json
import os
import subprocess
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

TOOLS = [
    {
        "name": "run_command",
        "description": "在电脑上执行命令(cmd/PowerShell)，返回输出。如: dir, ipconfig, whoami, echo hi",
        "inputSchema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
    },
    {
        "name": "list_dir",
        "description": "列出指定目录内容，默认当前目录",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}},
    },
    {
        "name": "read_file",
        "description": "读取文本文件内容(前5000字符)",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    },
    {
        "name": "write_file",
        "description": "写入文件(覆盖)。path用绝对路径如 D:/test/note.txt",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]},
    },
    {
        "name": "screenshot",
        "description": "用PowerShell截屏，保存到用户目录，返回文件路径",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def run_command(command: str) -> str:
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=90)
        return json.dumps({"exit": r.returncode, "stdout": (r.stdout or "")[:4000], "stderr": (r.stderr or "")[:1500]}, ensure_ascii=False)
    except Exception as e:
        return f"error: {e}"


def list_dir(path: str = ".") -> str:
    try:
        return "\n".join(os.listdir(path)[:300])
    except Exception as e:
        return f"error: {e}"


def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()[:5000]
    except Exception as e:
        return f"error: {e}"


def write_file(path: str, content: str) -> str:
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"written: {path}"
    except Exception as e:
        return f"error: {e}"


def screenshot() -> str:
    ps = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "Add-Type -AssemblyName System.Drawing; "
        "$b = New-Object System.Drawing.Bitmap([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height); "
        "$g = [System.Drawing.Graphics]::FromImage($b); "
        "$g.CopyFromScreen(0,0,0,0,$b.Size); "
        "$p = \"$env:USERPROFILE\\pc_shot.png\"; "
        "$b.Save($p); $p"
    )
    try:
        r = subprocess.run(["powershell", "-c", ps], capture_output=True, text=True, timeout=30)
        return (r.stdout or "").strip() or f"err: {r.stderr[:500]}"
    except Exception as e:
        return f"error: {e}"


class Handler(BaseHTTPRequestHandler):
    def _send(self, obj):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            self.send_response(202)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        method = body.get("method", "")
        req_id = body.get("id")

        # JSON-RPC通知（没有id，如 notifications/initialized）：规范要求不回应
        if req_id is None:
            self.send_response(202)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        if method == "initialize":
            result = {
                "protocolVersion": body.get("params", {}).get("protocolVersion", "2025-03-26"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "pc-mcp", "version": "2.0"},
            }
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            name = body["params"]["name"]
            args = body["params"].get("arguments", {}) or {}
            try:
                text = globals()[name](**args)
                result = {"content": [{"type": "text", "text": text}]}
            except Exception as e:
                result = {"content": [{"type": "text", "text": f"error: {e}"}]}
        else:
            result = {}

        self._send({"jsonrpc": "2.0", "id": req_id, "result": result})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print("pc-mcp 跑起来了，监听 0.0.0.0:8787")
    ThreadingHTTPServer(("0.0.0.0", 8787), Handler).serve_forever()
