# pc-mcp

布丁狗电脑的 MCP server：让林川连上 Windows。

## 用法

```
pip install fastmcp mss uvicorn
python pc_mcp.py
```

监听 0.0.0.0:8787（仅 tailnet 内网可达，公网不可达）。

## 工具

- run_command: 执行命令（cmd/PowerShell）
- list_dir: 列目录
- read_file: 读文件
- write_file: 写文件
- screenshot: 截屏

## 安全

只走 tailscale 内网；不要对公网开放 8787 端口。