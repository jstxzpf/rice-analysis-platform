# Rice Analysis Platform

本项目为水稻分析平台，包含前后端及相关服务，支持田间数据采集、分析与可视化。

## 目录结构

- `backend/`：后端服务（Python FastAPI，Celery，数据库等）
- `frontend/`：前端项目（Vue3 + Vite）
- `nginx/`：Nginx 配置
- `uploads/`：上传文件目录
- `docker-compose.yml`：一键部署配置
- `design.md`：设计文档
- `GEMINI.md`：Gemini 相关说明

## 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/jstxzpf/rice-analysis-platform.git
cd rice-analysis-platform
```

### 2. 后端环境
```bash
cd backend
pip install -r requirements.txt
# 启动 FastAPI 服务
python -m app.main
```

### 3. 前端环境
```bash
cd frontend
npm install
npm run dev
```

### 4. 其他
- 可使用 `docker-compose up` 一键启动所有服务
- 详细部署与开发说明请见各目录下 README 或文档

## 贡献
欢迎 issue、PR 与建议！

## License
MIT
