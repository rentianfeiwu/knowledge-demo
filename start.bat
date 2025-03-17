@echo off
echo 正在启动知识库演示系统...

:: 启动后端服务
start cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: 等待2秒，确保后端先启动
timeout /t 2 /nobreak > nul

:: 启动前端服务
start cmd /k "cd frontend && npm run dev"

echo 服务已启动!
echo 后端地址: https://localhost:8000
echo 前端地址: http://localhost:5173