#!/bin/bash

# 创建项目根目录
mkdir -p beauty-saas-v1
cd beauty-saas-v1

# 后端目录结构
mkdir -p backend/app/{api/endpoints,services}
mkdir -p backend/uploads
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/endpoints/__init__.py
touch backend/app/services/__init__.py
touch backend/uploads/.gitkeep

# 前端目录结构
mkdir -p frontend/src/{api,pages,utils,components}
touch frontend/.env
touch frontend/index.html
touch frontend/src/main.ts

# 复制所有文件内容
# 这里你可以使用之前的文件内容

# 后端扩展目录结构
mkdir -p backend/app/{core,models,middleware,utils}
touch backend/app/core/__init__.py
touch backend/app/models/__init__.py
touch backend/app/middleware/__init__.py
touch backend/app/utils/__init__.py

# 创建必要的核心文件
touch backend/app/core/config.py
touch backend/app/core/security.py
touch backend/app/core/database.py

# 创建模型文件
touch backend/app/models/user.py
touch backend/app/models/document.py
touch backend/app/models/conversation.py

# 创建中间件文件
touch backend/app/middleware/authentication.py
touch backend/app/middleware/rate_limiter.py

# 创建工具类文件
touch backend/app/utils/cache.py
touch backend/app/utils/logger.py
touch backend/app/utils/async_tasks.py

echo "项目结构创建完成！"