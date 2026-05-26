# 真选AI (TrueAI) — 新一代 AI 导航，懂你

[![Live](https://img.shields.io/badge/live-shiflowai.cloud-22d3ee)](https://www.shiflowai.cloud)
[![MCP](https://img.shields.io/badge/MCP-server-blueviolet)](./skills/trueai/SKILL.md)
[![Skill](https://img.shields.io/badge/agent-skill-orange)](./skills/trueai/SKILL.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

> 我来帮你省钱，我来帮你省时间。
> 数据实时、人工评测、无广告。
> 没有最好的，只有最适合你的。

TrueAI 是一个面向 AI 工具的 **智能体推荐 + 人工评测 + 对话式导航** 平台 MVP。
用户可以：

- 浏览按类目组织的 AI 工具卡片墙（带吊绳轻摆动效）
- 用对话的方式让 **"懂你"** 助手反问并推荐（流式 SSE）
- 查看多维排行榜，支持"用自然语言生成专属排名"
- 把最多 3 个工具加入对比抽屉，做并排多维对比
- 阅读 / 提交工具评测（审核通过后可获得现金奖励；MVP 仅保留表结构）

## 🤖 接入你的 AI Agent（MCP / Skill）

TrueAI 1600+ 应用目录已封装成 **MCP Server** 和 **单文件 Skill**，让你的
agent 直接获得"挑 AI 工具"的能力。完整文档：[`skills/trueai/SKILL.md`](./skills/trueai/SKILL.md)。

### 一行接入 MCP（Claude Desktop / Cursor / Cline / Continue / Windsurf）

```json
{ "mcpServers": { "trueai": { "url": "https://www.shiflowai.cloud/mcp" } } }
```

接入后 agent 立即获得 4 个工具：

| 工具 | 用途 |
|---|---|
| `recommend_ai_tools(description, top_k)` | 用户自然语言需求 → 推荐合适应用 |
| `get_ai_tool(name_or_url, include_reviews)` | 名称 / slug / 官网 URL → 应用完整信息 |
| `list_ai_tools(category, free_only, ...)` | 按分类 / 形态 / 是否免费 浏览目录 |
| `list_categories()` | 列出全部分类 |

### 无 MCP 也能用——drop-in skill 文件

把 [`skills/trueai/SKILL.md`](./skills/trueai/SKILL.md) 复制到任意 agent 的 skills 目录，
agent 就会按文档里 curl 示例直接调 `https://www.shiflowai.cloud/api/*`。

### 数据 schema

每个 AI 应用 34 个结构化字段（评分 / 价格 / 形态 / 评论 / 链接 …），
完整 JSON Schema：[`docs/ai_tool_schema.json`](./docs/ai_tool_schema.json)。

## 技术栈

| 层 | 选型 |
| --- | --- |
| 后端 | Python 3.10+ / FastAPI 0.115 / SQLAlchemy 2 / Alembic / PyMySQL |
| 前端 | Next.js 14 (App Router, 纯 JavaScript) / Tailwind CSS / Framer Motion / Zustand |
| 数据库 | MySQL 8 (`114.55.254.123:3306/trueai`) |
| LLM | 阿里云 DashScope (`qwen-plus`)，未配置 Key 时自动回退 Mock 文案 |
| 鉴权 | JWT (python-jose) + bcrypt |

## 目录结构

```
TrueAI/
├── backend/              # FastAPI 服务
│   ├── app/
│   │   ├── core/         # 配置 / DB / 安全
│   │   ├── models/       # ORM 模型
│   │   ├── schemas/      # Pydantic
│   │   ├── api/routers/  # auth / categories / tools / reviews / rankings / stats / search
│   │   ├── services/llm/ # Qwen 与 Mock 两种 Provider
│   │   ├── services/recommend.py  # 意图抽取 + MySQL 候选召回
│   │   └── seeds/seed_tools.py
│   ├── alembic/
│   └── requirements.txt
└── frontend/             # Next.js 14
    ├── app/              # layout / page / category / tool / search / rankings / compare / earn
    ├── components/       # NavBar / HeroTypewriter / Sidebar / ToolCard / CompareBar / ChatSearch ...
    ├── lib/              # api.js / compareStore.js / labels.js
    └── tailwind.config.js
```

## 快速开始

> 前提：已安装 Python 3.10+、Node 20+、能访问 MySQL `114.55.254.123:3306`。

### 1. 后端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # 按需改 JWT_SECRET / DASHSCOPE_API_KEY

# 首次：执行数据库迁移 + 种子数据
alembic upgrade head
python -m app.seeds.seed_tools

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# http://localhost:8000/docs 查看 OpenAPI
```

### 2. 前端

```bash
cd frontend
npm install
cp .env.local.example .env.local   # 默认指向 http://127.0.0.1:8000
npm run dev
# 打开 http://localhost:3000
```

## 环境变量

### `backend/.env`

| 变量 | 说明 |
| --- | --- |
| `DATABASE_URL` | 形如 `mysql+pymysql://user:pass@host:3306/trueai`，密码中特殊字符需 URL 编码（`@` → `%40`） |
| `JWT_SECRET` | JWT 签名密钥，生产请替换为长随机串 |
| `JWT_EXPIRES_MINUTES` | token 过期分钟数，默认 7 天 |
| `LLM_PROVIDER` | `qwen`（默认）。为空或 Key 缺失时自动回退 Mock |
| `DASHSCOPE_API_KEY` | 通义千问 Key，在 [DashScope 控制台](https://dashscope.console.aliyun.com/) 创建 |
| `QWEN_MODEL` | 默认 `qwen-plus`，可换成 `qwen-turbo` / `qwen-max` |
| `CORS_ORIGINS` | 允许的前端 origin，逗号分隔 |

### `frontend/.env.local`

| 变量 | 说明 |
| --- | --- |
| `NEXT_PUBLIC_API_BASE` | 后端 Base URL，开发默认 `http://127.0.0.1:8000` |

> 前端所有 `/api/*` 请求在 Next.js 端通过 `rewrites` 代理到后端，避免浏览器 CORS 问题。

## 核心 API

| 接口 | 说明 |
| --- | --- |
| `GET /api/health` | 健康检查 |
| `GET /api/stats` | 首页横幅用：工具数 / 分类数 / 评测数 / 价值观文案 |
| `GET /api/categories` | 全部分类 + 每类工具数 |
| `GET /api/tools` | 列表 + 多维筛选 + 排序 + 分页 |
| `GET /api/tools/{id 或 slug}` | 智能体详情 |
| `POST /api/tools/compare` | 对比（body 为 id 列表） |
| `GET /api/rankings?dimension=&category=&top=` | 排行榜 |
| `POST /api/reviews` | 提交评测（需 Bearer token） |
| `GET /api/reviews?tool_id=&status_filter=approved` | 评测列表 |
| `POST /api/search/chat` | 对话搜索，SSE 流：`event: meta` + 多个 `event: delta` + `event: done` |
| `GET /api/search/chat?q=...` | 非流式兜底：直接给候选和外部导航 |
| `POST /api/auth/register` / `/login` / `GET /api/auth/me` | 注册 / 登录 / 查询当前用户 |

种子数据自带一个管理员账号：`admin / admin123456`（生产请删除或改密）。

## "懂你"对话搜索的工作方式

1. 客户端把当前会话（含历史）`POST` 到 `/api/search/chat`。
2. 后端根据最新 user 消息，用关键词字典抽取 **类目 / 人群 / 免费 / 国内直连** 等意图。
3. 先从 MySQL 召回 ≤ 6 个候选，立即通过 `event: meta` 推送给前端（前端马上渲染卡片）。
4. 接着把系统 Prompt + 候选摘要 + 会话历史交给 Qwen 流式输出，按字/片推送 `event: delta`。
5. 若候选为空，`meta` 中带 `external` 外部 AI 导航站清单，前端展示"去别家看看"。

## 常见问题

- **`ValueError: invalid interpolation syntax`**：Alembic 读 `%` 会报错。`alembic/env.py` 已做 `%` → `%%` 转义。
- **`pymysql` 连接慢 / 超时**：`pool_pre_ping=True`、`pool_recycle=3600` 已打开；请确认 MySQL 白名单已允许你的出口 IP。
- **前端 API 跨域**：开发期通过 `next.config.js` rewrites 代理，无需额外处理。部署时建议把后端放到同域 `/api/*` 路径下。
- **Qwen 没配 Key**：`/api/search/chat` 会自动回退到 Mock Provider，候选卡片依然是真实数据，只是 AI 文案是占位。

## 下一步（非 MVP）

- 任务 / 赏金系统：管理员发布任务 → 用户领取评测 → 后台审核 → 微信提现
- 用户自发布任务
- 评测通过后自动刷新工具的综合评分
- 微信登录 + 手机号登录
- 工具增删改的管理后台

MIT License.
