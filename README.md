# pc-mcp

布丁狗电脑的 MCP server：让林川连上 Windows。

## 用法（v2 纯标准库版，零依赖）

```
python pc_mcp.py
```

任何 Python 版本直接跑，不需要装任何包。监听 0.0.0.0:8787（仅 tailnet 内网可达）。

## 工具

- run_command: 执行命令（cmd/PowerShell）
- list_dir: 列目录
- read_file: 读文件
- write_file: 写文件
- screenshot: 截屏（PowerShell）

## MCP 协议

最小实现：initialize / tools/list / tools/call（Streamable HTTP）。

## 安全

只走 tailscale 内网；不要对公网开放 8787 端口。