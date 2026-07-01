# Placement Journal — MVP

社工实习记录系统，MVP 阶段：登录 + 实习记录（Placement Log）+ Reflection Note + Dashboard。
Case Note / Review-Feedback / Supervisor 角色的数据结构已预留，尚未开放对应 API 和界面。

## 目录结构

```
placement-tracker/
├── backend/       FastAPI + PostgreSQL
└── frontend/      React + Vite + Tailwind
```

## 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # 按需修改 JWT_SECRET 等
docker compose up -d               # 启动本地 PostgreSQL（如果你已有生产数据库，跳过这步，改 .env 里的 DATABASE_URL）

uvicorn app.main:app --reload --port 8000
```

首次启动会自动建表。因为不开放注册，用以下脚本创建第一个账号：

```bash
python -m app.seed --username alice --password "一个强密码" --full-name "Alice Chen" --role student
```

访问 http://localhost:8000/docs 可以看到自动生成的 API 文档。

## 前端启动

```bash
cd frontend
npm install
cp .env.example .env               # 确认 VITE_API_BASE 指向你的后端地址
npm run dev
```

访问 http://localhost:5173，用刚才创建的账号登录。

## 部署到你自己的服务器（要点）

1. 后端：用 `gunicorn -k uvicorn.workers.UvicornWorker app.main:app` 或直接 `uvicorn` 起进程，配合 `systemd` 保活；`.env` 里 `JWT_SECRET` 一定要换成随机字符串，不要用示例值。
2. 前端：`npm run build` 产出静态文件（`dist/`），交给 Nginx 直接托管。
3. Nginx 反代 `/api/` 到后端端口，静态文件走前端 `dist/`；记得给上传接口放宽 `client_max_body_size`（默认 1MB 太小，建议设到比 `MAX_UPLOAD_SIZE_MB` 大一点，比如 20m）。
4. 附件目前存本地磁盘（`UPLOAD_DIR`），记得把这个目录纳入你的备份范围，同时定时 `pg_dump` 备份数据库。
5. CORS：`.env` 的 `CORS_ORIGINS` 要改成你的正式域名，不要留 localhost。

## 已预留、MVP 阶段未启用的扩展点

- `case_notes` / `case_note_links` 表：Case Note 功能的数据结构，字段参考了社工记录常见要素（presenting issue / intervention / plan / risk assessment / 结案说明），后续直接加 router + 前端页面即可，不需要改表结构。
- `feedback` 表：督导审核反馈，`is_read` 字段用于 Dashboard 的 todo 提醒。
- `supervisor_interns` 表：督导与实习生的绑定关系，目前是空表。
- `placement_logs` / `reflection_notes` 的 `status` 和 `reviewer_id` 字段：目前恒为 `draft`，加上 review 功能后可以直接用。
- 后端所有权限校验目前只做了"自己的记录自己改"，督导跨用户查看的权限逻辑要在加 supervisor 功能时一并实现，不要只在前端隐藏入口。
