# 项目进度记录本

**项目名称**: StepWise (苏格拉底式数学辅导系统)
**最后更新**: 2026-01-09 22:05

---

## 最新进度（倒序记录，最新的在最上面）

### [2026-01-09 22:05] - Docker 容器化部署完成

- [x] **修复 Frontend 健康检查**: 修改 Dockerfile 健康检查使用 IPv4 (frontend/Dockerfile:38)
- [x] **Backend 容器部署**: 成功运行在 8000 端口，健康检查通过
- [x] **Frontend 容器部署**: 成功运行在 3000 端口，健康检查通过
- [x] **端点验证**: 所有 HTTP 端点返回 200 状态码

> **遇到的坑**:
> **Frontend 健康检查失败（IPv6 问题）**
>
> - **现象**: 容器显示 unhealthy，但外部访问正常（200）
> - **原因**: wget 默认尝试 IPv6 [::1]，但 nginx 只监听 IPv4
> - **解决**: 健康检查改用 `127.0.0.1:8080` 强制 IPv4
> - **教训**: 容器内健康检查需要显式指定 IP 协议版本

> **Docker 容器信息**:
>
> - **Backend**: `docker run -d --name stepwise-backend -p 8000:8000 -e EMAIL_PROVIDER=console -e API_ACCESS_KEY=dev-test-key -e BETA_ACCESS_CODE=MATH2024 stepwise-backend`
> - **Frontend**: `docker run -d --name stepwise-frontend -p 3000:8080 stepwise-frontend`
> - **数据持久化**: 使用 SQLite (`/data/stepwise.db` 在容器内)

### [2026-01-09 21:30] - GitHub 分支保护和 Private Beta 招募材料

- [x] **分支保护配置**: 要求 backend 和 frontend CI 检查通过才能合并
- [x] **仓库可见性**: 改为 public（分支保护需要）
- [x] **Private Beta 招募材料**: 生成 Reddit 帖子、Discord 消息、邮件模板、PMF 调查问卷、合规页脚

> **技术选型**:
>
> - **分支保护策略**: 严格模式 + 强制管理员遵守 + 禁止强制推送
> - **目标用户**: 美国 20-50 个家庭，K-12 学生家长

### [2026-01-09 20:00] - CI 管道修复（全部通过）

- [x] **依赖修复**: 添加 email-validator, reportlab, alembic 到 pyproject.toml
- [x] **包发现修复**: 改用 setuptools 自动包发现机制
- [x] **E2E 测试修复**: 从项目根运行 uvicorn，使用 backend.main:app
- [x] **CI 状态**: Backend 267 passed, Frontend 38 passed ✅

> **遇到的坑**:
> **模块导入路径问题**
>
> - **现象**: CI 报 `ModuleNotFoundError: No module named 'backend'`
> - **尝试**: 修改 Playwright config 的 working directory（失败）
> - **解决**: 从项目根运行 uvicorn，使用 `backend.main:app` 而非 `main:app`
> - **教训**: Python 模块路径取决于脚本运行位置，代码中的 import 必须匹配

> **技术选型**:
>
> - **包管理**: setuptools 自动发现优于显式列表（更灵活）
> - **CI 运行位置**: 从项目根统一管理，避免路径混乱

### [2026-01-09 18:00] - GitHub Release 和初始发布

- [x] **创建 Release**: v0.1.1 发布到 GitHub
- [x] **Git 配置**: 配置 remote 到 https://github.com/412984588/stepwise
- [x] **测试验收**: Backend 267 passed, E2E 38 passed
- [x] **Git Tag**: 创建并推送 v0.1.1 标签

> **发布信息**:
>
> - **版本号**: v0.1.1
> - **发布 URL**: https://github.com/412984588/stepwise/releases/tag/v0.1.1
> - **CI URL**: https://github.com/412984588/stepwise/actions/runs/20853960798

---

## 关键里程碑

1. ✅ **完整功能开发** - 苏格拉底式数学辅导系统
2. ✅ **测试覆盖** - 305 个测试（267 backend + 38 E2E）
3. ✅ **CI/CD 管道** - 自动化测试和部署
4. ✅ **分支保护** - 代码质量门禁
5. ✅ **Docker 部署** - 容器化生产就绪
6. ⏳ **Private Beta** - 招募 20-50 美国家庭

---

## 技术栈总结

- **后端**: Python 3.11, FastAPI, SQLite, Pydantic, OpenAI API
- **前端**: React 18, TypeScript, Vite, Material-UI
- **测试**: Pytest (backend), Playwright (E2E)
- **部署**: Docker (multi-stage build), nginx
- **CI/CD**: GitHub Actions
- **工具**: Git, GitHub CLI, Black, Flake8

---

## 下一步计划

- [ ] **生产部署**: 部署到 Railway/Fly.io/Vercel
- [ ] **数据持久化**: 配置 Docker volume 挂载
- [ ] **环境配置**: 生产环境变量管理
- [ ] **监控**: 添加日志和监控工具
- [ ] **Private Beta**: 启动招募并收集反馈
- [ ] **数据库迁移**: 考虑从 SQLite 迁移到 PostgreSQL（生产环境）
