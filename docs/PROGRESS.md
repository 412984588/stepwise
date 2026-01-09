# 项目进度记录本

**项目名称**: StepWise - 苏格拉底式数学辅导系统
**最后更新**: 2026-01-09 23:50

---

## 最新进度（倒序记录，最新的在最上面）

### [2026-01-09 23:50] - PostgreSQL 开发环境集成成功

- [x] **核心修复**: 修复数据库模型外键类型不匹配问题 (backend/models/solution.py)
- [x] **PostgreSQL 集成**: 成功集成 PostgreSQL 到 Docker 开发环境
- [x] **依赖更新**: 添加 psycopg2-binary 支持 PostgreSQL
- [x] **数据库验证**: 所有 12 个表成功创建，外键约束正确设置

> **遇到的坑**:
> **数据库模型外键类型不匹配**
>
> - **现象**: PostgreSQL 报错 "foreign key constraint cannot be implemented, types: integer vs varchar"
> - **原因**: BaseModel 使用 String(36) UUID 作为主键，但 FullSolution 的 problem_id 使用 Integer
> - **解决**:
>   1. 删除 FullSolution 中对 id 的重写（继承 BaseModel 的 UUID）
>   2. 将 problem_id 改为 String(36) 匹配 Problem.id
>   3. 删除重复的 created_at 定义（BaseModel 已提供）
> - **教训**: SQLite 类型检查宽松，PostgreSQL 严格检查外键类型匹配

> **技术选型**:
>
> - **PostgreSQL 16 Alpine**: 轻量级官方镜像，占用空间小
> - **psycopg2-binary**: Python PostgreSQL 适配器，安装简单
> - **Docker Compose Profiles**: 使用 `--profile postgres` 条件启用服务
> - **端口映射**: 5433:5432 避免与宿主机其他 PostgreSQL 实例冲突

### [2026-01-09] - 之前的进展

- Beta 邀请码管理系统 (PR #2)
- Docker 开发环境 (PR #3)
- CI/CD 流水线修复
- GitHub Release v0.1.1
- 分支保护规则设置
