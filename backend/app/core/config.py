from pathlib import Path

class Settings:
    # 项目根目录
    BASE_DIR = Path(__file__).parent.parent.parent
    
    # HTTPS 配置
    SSL_KEYFILE = BASE_DIR / "key.pem"
    SSL_CERTFILE = BASE_DIR / "cert.pem"
    
    # CORS 配置
    CORS_ORIGINS = [
        "http://localhost:5173",
        "https://localhost:5173",
        "http://127.0.0.1:5173",
        "http://172.22.48.1:5173",  # 替换为实际的服务器IP
        "https://172.22.48.1:5173",  # 替换为实际的服务器IP
        "http://0.0.0.0:5173",
        "https://0.0.0.0:5173"
    ]

settings = Settings()