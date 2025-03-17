from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.endpoints import assistant, knowledge, analytics, speech
from app.core.services import file_service
from app.core.config import settings
import time


class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


app = FastAPI(title="Beauty SaaS API")

# 添加超时中间件
app.add_middleware(TimeoutMiddleware)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """服务启动时自动重建索引"""
    print("=== 服务启动，开始重建索引 ===")
    try:
        file_service.rebuild_index()
        print("=== 索引重建完成 ===")
    except Exception as e:
        print(f"=== 索引重建失败: {str(e)} ===")

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(assistant.router, prefix="/api", tags=["assistant"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
# 修正：直接使用app注册speech路由
app.include_router(speech.router, prefix="/api/speech", tags=["speech"])

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        ssl_keyfile=str(settings.SSL_KEYFILE),
        ssl_certfile=str(settings.SSL_CERTFILE)
    )
