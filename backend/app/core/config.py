from pathlib import Path

class Settings:
    # 项目根目录
    BASE_DIR = Path(__file__).parent.parent.parent
    
    # HTTPS 配置
    SSL_KEYFILE = BASE_DIR / "key.pem"
    SSL_CERTFILE = BASE_DIR / "cert.pem"
    
    # CORS 配置
    CORS_ORIGINS = [
        "https://localhost:5173",
        "http://localhost:5173",
        "https://172.22.48.1:5173",
        "http://172.22.48.1:5173",
        "https://192.168.1.42:5173",
        "http://192.168.1.42:5173"
    ]

settings = Settings() 