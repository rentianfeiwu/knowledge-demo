# 知识库演示系统

基于本地模型，及python工具库whoosh的智能问答系统，支持文档上传、语音识别和智能搜索。

## 功能特点

- 文档上传与管理
- 智能搜索与问答
- 语音识别输入
- 数据可视化展示

## 技术栈

- 前端：Vue 3 + TypeScript + Ant Design Vue
- 后端：FastAPI + Python
- 向量数据库：FAISS
- 语音识别：百度语音识别API

## 快速开始

### 环境要求

- Node.js 16+
- Python 3.8+
- 百度语音识别API密钥（可选）

### 安装依赖

1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt

2. 安装前端依赖
```bash
cd frontend
npm install

语音配置
在 backend 目录下创建 .env 文件，添加以下内容
BAIDU_API_KEY=您的百度API密钥
BAIDU_SECRET_KEY=您的百度Secret密钥

启动服务
使用一键启动脚本：
```bash
./start.sh

或者分别启动：
- 后端： cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
- 前端： cd frontend && npm run dev

使用说明
1. 访问前端页面： http://localhost:5173/base-demo
2. 上传文档：支持PDF、Word文档
3. 提问：在搜索框中输入问题或使用语音输入
4. 查看回答：系统会基于上传的文档内容生成回答