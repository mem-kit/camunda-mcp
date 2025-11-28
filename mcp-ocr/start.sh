#!/bin/bash

# python3 -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt
# 激活虚拟环境
source venv/bin/activate

# 后台运行 uvicorn，并将输出重定向到日志文件
nohup python ocr_mcp.py --reload > mcp.log 2>&1 &

# 保存进程 ID
echo $! > mcp.pid

echo "OCR MCP 已在后台启动"
echo "进程 ID: $(cat mcp.pid)"
echo "日志文件: mcp.log"
echo "停止服务请运行: kill \$(cat mcp.pid)"
