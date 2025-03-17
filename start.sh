#!/bin/bash
echo "正在启动知识库演示系统..."

# 启动后端服务
cd backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

# 等待2秒
sleep 2

# 启动前端服务
cd ../frontend
nohup npm run dev -- --host 0.0.0.0 > frontend.log 2>&1 &

echo "服务已启动!"
echo "后端地址: https://服务器IP:8000"
echo "前端地址: http://服务器IP:5173"