# StepWise Development Environment

开发环境使用 Docker Compose 配置，提供热重载和快速开发体验。

## 🚀 快速启动

### 启动开发环境

```bash
# 构建并启动所有服务
docker compose -f docker-compose.dev.yml up --build

# 后台运行
docker compose -f docker-compose.dev.yml up -d --build
```

### 停止开发环境

```bash
# 停止所有服务
docker compose -f docker-compose.dev.yml down

# 停止并删除数据卷
docker compose -f docker-compose.dev.yml down -v
```

## 📦 服务清单

| 服务         | 端口      | 描述                       | URL                        |
| ------------ | --------- | -------------------------- | -------------------------- |
| **Backend**  | 8000      | FastAPI + Uvicorn (热重载) | http://localhost:8000      |
| **Frontend** | 3000      | React + Vite (HMR)         | http://localhost:3000      |
| **API Docs** | 8000/docs | Swagger UI                 | http://localhost:8000/docs |

## 🔧 开发特性

### Backend (FastAPI)

- ✅ **热重载**: 代码修改自动重启服务器
- ✅ **Volume 挂载**: `./backend` → `/app/backend`
- ✅ **开发依赖**: pytest, black, ruff, mypy 等
- ✅ **环境变量**:
  - `EMAIL_PROVIDER=console` (邮件输出到控制台)
  - `API_ACCESS_KEY=dev-test-key`
  - `BETA_ACCESS_CODE=MATH2024`
  - `DATABASE_URL=sqlite:////data/stepwise_dev.db`

### Frontend (React + Vite)

- ✅ **HMR**: 热模块替换，秒级更新
- ✅ **Volume 挂载**: `./frontend` → `/app`
- ✅ **node_modules**: 使用容器版本（不挂载）
- ✅ **API 代理**: `VITE_API_BASE_URL=http://localhost:8000`

## 📝 常用命令

### 查看日志

```bash
# 所有服务
docker compose -f docker-compose.dev.yml logs -f

# 单个服务
docker compose -f docker-compose.dev.yml logs -f backend
docker compose -f docker-compose.dev.yml logs -f frontend
```

### 重启服务

```bash
# 重启单个服务
docker compose -f docker-compose.dev.yml restart backend
docker compose -f docker-compose.dev.yml restart frontend

# 重新构建并重启
docker compose -f docker-compose.dev.yml up -d --build backend
```

### 进入容器

```bash
# Backend shell
docker compose -f docker-compose.dev.yml exec backend bash

# Frontend shell
docker compose -f docker-compose.dev.yml exec frontend sh
```

### 运行测试

```bash
# Backend 测试
docker compose -f docker-compose.dev.yml exec backend pytest

# Frontend E2E 测试（需要在宿主机运行）
cd frontend && npm test
```

## 🗄️ 数据持久化

开发环境使用 Docker volume 持久化 SQLite 数据库：

```bash
# 查看 volume
docker volume ls | grep stepwise-dev-data

# 清除数据（重置数据库）
docker compose -f docker-compose.dev.yml down -v
```

**数据库位置**: `/data/stepwise_dev.db` (容器内)

## 🔄 热重载工作原理

### Backend (Uvicorn --reload)

```bash
uvicorn backend.main:app \\
  --host 0.0.0.0 \\
  --port 8000 \\
  --reload \\
  --reload-dir /app/backend
```

- 监听 `./backend` 目录下所有文件变化
- 自动重启服务器（1-2秒）
- 保留应用状态（数据库连接等）

### Frontend (Vite HMR)

```bash
npm run dev -- --host 0.0.0.0 --port 3000
```

- 监听 `./frontend` 目录下所有文件变化
- 热模块替换（无需刷新页面）
- 保留组件状态

## 🐛 故障排查

### 端口冲突

```bash
# 检查端口占用
lsof -i :8000
lsof -i :3000

# 停止冲突的容器
docker stop stepwise-backend stepwise-frontend
```

### 容器无法启动

```bash
# 查看详细日志
docker compose -f docker-compose.dev.yml logs backend
docker compose -f docker-compose.dev.yml logs frontend

# 重新构建
docker compose -f docker-compose.dev.yml build --no-cache backend
```

### 代码修改不生效

**Backend**:

- 检查 volume 挂载: `docker compose -f docker-compose.dev.yml config`
- 重启服务: `docker compose -f docker-compose.dev.yml restart backend`

**Frontend**:

- 清除缓存: `rm -rf frontend/node_modules/.vite`
- 重新构建: `docker compose -f docker-compose.dev.yml up -d --build frontend`

### 健康检查失败

```bash
# 查看健康检查日志
docker inspect stepwise-backend-dev --format='{{json .State.Health}}' | jq
docker inspect stepwise-frontend-dev --format='{{json .State.Health}}' | jq

# Frontend 健康检查可能失败（wget 不可用），但不影响开发
```

## 📊 性能对比

| 模式           | 启动时间 | 代码修改生效                     | 内存占用 |
| -------------- | -------- | -------------------------------- | -------- |
| **Docker Dev** | ~30s     | 1-2s (Backend) / 即时 (Frontend) | ~500MB   |
| **本地运行**   | ~5s      | 即时                             | ~200MB   |

**建议**:

- **日常开发**: 本地运行（更快）
- **测试部署**: Docker Dev（环境一致）
- **团队协作**: Docker Dev（避免环境差异）

## 🔗 相关文件

- `docker-compose.dev.yml` - 开发环境配置
- `backend/Dockerfile.dev` - Backend 开发镜像
- `frontend/Dockerfile.dev` - Frontend 开发镜像
- `backend/Dockerfile` - Backend 生产镜像
- `frontend/Dockerfile` - Frontend 生产镜像

## 🚀 生产环境

开发完成后，使用生产 Dockerfile 构建：

```bash
# Backend
docker build -t stepwise-backend -f backend/Dockerfile .

# Frontend
docker build -t stepwise-frontend -f frontend/Dockerfile frontend

# 运行生产容器
docker run -d --name stepwise-backend -p 8000:8000 \\
  -e EMAIL_PROVIDER=console \\
  -e API_ACCESS_KEY=dev-test-key \\
  stepwise-backend

docker run -d --name stepwise-frontend -p 3000:8080 \\
  stepwise-frontend
```

## 💡 开发技巧

### 使用 VS Code Remote Containers

1. 安装 "Dev Containers" 扩展
2. `Ctrl+Shift+P` → "Attach to Running Container"
3. 选择 `stepwise-backend-dev` 或 `stepwise-frontend-dev`
4. 在容器内直接编辑代码

### 使用 Debugger

**Backend (pdb)**:

```python
import pdb; pdb.set_trace()
```

然后 attach 到容器:

```bash
docker attach stepwise-backend-dev
```

**Frontend (Chrome DevTools)**:

- 浏览器打开 `http://localhost:3000`
- F12 打开开发者工具
- Sources 面板设置断点

### 环境变量覆盖

创建 `.env.dev` 文件（已加入 .gitignore）:

```bash
# .env.dev
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

修改 `docker-compose.dev.yml`:

```yaml
services:
  backend:
    env_file:
      - .env.dev
```

## 📚 延伸阅读

- [FastAPI 文档](https://fastapi.tiangolo.com)
- [Vite 文档](https://vitejs.dev)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Uvicorn 热重载](https://www.uvicorn.org/#command-line-options)
