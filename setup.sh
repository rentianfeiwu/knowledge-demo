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

echo "项目结构创建完成！" 