"""TrueAI 种子数据：分类 + 智能体/工具。

分类参考 https://hao.uisdc.com/ai 的主类目，稍作本土化合并。
工具覆盖当前主流真实产品，字段尽量如实填写；评分 0-10 为编辑部初始印象分，可被后续真实评测覆盖。

用法：
    python -m app.seeds.seed_tools
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.db import SessionLocal, engine
from app.models import Category, Tool, ToolAudience, ToolCategory
from app.models.user import User
from app.core.security import hash_password


CATEGORIES: list[dict] = [
    {"slug": "chat", "name": "对话聊天", "icon": "💬", "sort_order": 1},
    {"slug": "coding", "name": "编程开发", "icon": "💻", "sort_order": 2},
    {"slug": "writing", "name": "写作文案", "icon": "✍️", "sort_order": 3},
    {"slug": "image", "name": "AI 绘画", "icon": "🎨", "sort_order": 4},
    {"slug": "video", "name": "AI 视频", "icon": "🎬", "sort_order": 5},
    {"slug": "audio", "name": "语音音乐", "icon": "🎵", "sort_order": 6},
    {"slug": "design", "name": "设计工具", "icon": "🖌️", "sort_order": 7},
    {"slug": "office", "name": "办公提效", "icon": "📊", "sort_order": 8},
    {"slug": "search", "name": "AI 搜索", "icon": "🔍", "sort_order": 9},
    {"slug": "agent", "name": "AI 智能体", "icon": "🤖", "sort_order": 10},
    {"slug": "translate", "name": "翻译语言", "icon": "🌐", "sort_order": 11},
    {"slug": "learning", "name": "学习教育", "icon": "🎓", "sort_order": 12},
]


TOOLS: list[dict] = [
    # ---------- 对话聊天 ----------
    {
        "name": "ChatGPT", "slug": "chatgpt", "tagline": "OpenAI 出品的对话式通用 AI 助手",
        "description": "全球最知名的通用大模型对话产品，支持 GPT-4o，擅长编程、写作、翻译、图像识别等。",
        "developer": "OpenAI", "launched_at": date(2022, 11, 30),
        "form_factor": "saas", "is_free": True, "pricing_info": "免费版可用；Plus $20/月",
        "need_vpn": True, "support_cli": False, "support_api": True,
        "official_url": "https://chatgpt.com",
        "logo_url": "https://cdn.oaistatic.com/assets/favicon-eex17e9e.svg",
        "overall_score": 9.3, "usability_score": 9.5, "effect_score": 9.5, "price_score": 7.5, "speed_score": 9.0,
        "categories": ["chat", "writing"], "audiences": ["beginner", "developer", "designer"],
    },
    {
        "name": "Claude", "slug": "claude", "tagline": "Anthropic 旗下的长上下文写作/编程利器",
        "description": "以长文本、写作质量和代码能力著称，200K 上下文，对中文语感自然。",
        "developer": "Anthropic", "launched_at": date(2023, 3, 14),
        "form_factor": "saas", "is_free": True, "pricing_info": "免费版可用；Pro $20/月",
        "need_vpn": True, "support_cli": True, "support_api": True,
        "official_url": "https://claude.ai",
        "logo_url": "https://claude.ai/favicon.ico",
        "overall_score": 9.2, "usability_score": 9.3, "effect_score": 9.5, "price_score": 7.5, "speed_score": 8.8,
        "categories": ["chat", "writing", "coding"], "audiences": ["developer", "designer"],
    },
    {
        "name": "通义千问", "slug": "qwen", "tagline": "阿里云出品的中文大模型",
        "description": "阿里通义系列，Qwen 开源生态丰富，网页端支持文档/图片/代码，企业侧合规。",
        "developer": "阿里云", "launched_at": date(2023, 4, 7),
        "form_factor": "saas", "is_free": True, "pricing_info": "网页端免费；API 按量",
        "need_vpn": False, "support_cli": False, "support_api": True,
        "official_url": "https://tongyi.aliyun.com",
        "logo_url": "https://img.alicdn.com/imgextra/i1/O1CN01Rp5cMJ1WpWgBvJEf6_!!6000000002837-2-tps-512-512.png",
        "overall_score": 8.5, "usability_score": 9.0, "effect_score": 8.5, "price_score": 9.0, "speed_score": 8.5,
        "categories": ["chat", "writing"], "audiences": ["beginner", "developer"],
    },
    {
        "name": "DeepSeek", "slug": "deepseek", "tagline": "深度求索，高性价比推理模型",
        "description": "DeepSeek-V3 / R1 推理能力强且价格极低，国内直连，支持联网搜索。",
        "developer": "深度求索", "launched_at": date(2023, 11, 2),
        "form_factor": "saas", "is_free": True, "pricing_info": "网页端免费；API 输入 1 元/百万 token",
        "need_vpn": False, "support_cli": False, "support_api": True,
        "official_url": "https://chat.deepseek.com",
        "logo_url": "https://chat.deepseek.com/favicon.svg",
        "overall_score": 9.0, "usability_score": 9.0, "effect_score": 9.3, "price_score": 9.8, "speed_score": 8.5,
        "categories": ["chat", "coding"], "audiences": ["developer", "beginner", "student"],
    },
    {
        "name": "Kimi", "slug": "kimi", "tagline": "月之暗面，超长文阅读理解",
        "description": "擅长长文档总结、论文阅读，支持 200 万字上下文，网页端响应快。",
        "developer": "月之暗面", "launched_at": date(2023, 10, 9),
        "form_factor": "saas", "is_free": True, "pricing_info": "网页端免费",
        "need_vpn": False, "support_cli": False, "support_api": True,
        "official_url": "https://kimi.moonshot.cn",
        "logo_url": "https://statics.moonshot.cn/kimi-chat/favicon.ico",
        "overall_score": 8.7, "usability_score": 9.2, "effect_score": 8.8, "price_score": 9.5, "speed_score": 8.8,
        "categories": ["chat", "learning"], "audiences": ["student", "beginner"],
    },
    {
        "name": "豆包", "slug": "doubao", "tagline": "字节跳动的日常 AI 助手",
        "description": "字节出品，支持语音对话、角色扮演，App 移动端体验优秀。",
        "developer": "字节跳动", "launched_at": date(2023, 8, 17),
        "form_factor": "mobile", "is_free": True, "pricing_info": "完全免费",
        "need_vpn": False, "support_cli": False, "support_api": True,
        "official_url": "https://www.doubao.com",
        "logo_url": "https://sf3-static.bytednsdoc.com/obj/eden-cn/ljhwZthlaukjlkulzlp/doubao.png",
        "overall_score": 8.3, "usability_score": 9.3, "effect_score": 8.0, "price_score": 10.0, "speed_score": 8.5,
        "categories": ["chat"], "audiences": ["beginner", "child", "senior"],
    },
    {
        "name": "文心一言", "slug": "ernie-bot", "tagline": "百度出品的中文大模型",
        "description": "文心 4.0 支持插件市场、文档/图片理解，生态完整。",
        "developer": "百度", "launched_at": date(2023, 3, 16),
        "form_factor": "saas", "is_free": True, "pricing_info": "基础免费；Plus 49.9/月",
        "need_vpn": False, "support_cli": False, "support_api": True,
        "official_url": "https://yiyan.baidu.com",
        "logo_url": "https://nlp-eb.cdn.bcebos.com/logo/favicon.ico",
        "overall_score": 7.8, "usability_score": 8.5, "effect_score": 7.8, "price_score": 8.0, "speed_score": 8.0,
        "categories": ["chat"], "audiences": ["beginner"],
    },
    {
        "name": "Gemini", "slug": "gemini", "tagline": "Google 多模态旗舰大模型",
        "description": "深度集成 Google 服务，支持图像、音频、视频理解，编程能力不俗。",
        "developer": "Google", "launched_at": date(2023, 12, 6),
        "form_factor": "saas", "is_free": True, "pricing_info": "免费；Advanced $20/月",
        "need_vpn": True, "support_cli": True, "support_api": True,
        "official_url": "https://gemini.google.com",
        "logo_url": "https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg",
        "overall_score": 8.8, "usability_score": 9.0, "effect_score": 9.0, "price_score": 7.5, "speed_score": 9.0,
        "categories": ["chat", "coding", "image"], "audiences": ["developer"],
    },

    # ---------- 编程开发 ----------
    {
        "name": "Cursor", "slug": "cursor", "tagline": "AI 优先的智能代码编辑器",
        "description": "基于 VS Code 的 AI IDE，Composer / Agent 模式可自主改代码、跑命令。",
        "developer": "Anysphere", "launched_at": date(2023, 3, 14),
        "form_factor": "windows_app", "is_free": True, "pricing_info": "免费有限；Pro $20/月",
        "need_vpn": False, "support_cli": True, "support_api": False,
        "official_url": "https://cursor.com",
        "logo_url": "https://cursor.com/favicon.ico",
        "overall_score": 9.5, "usability_score": 9.3, "effect_score": 9.6, "price_score": 7.8, "speed_score": 9.2,
        "categories": ["coding"], "audiences": ["developer"],
    },
    {
        "name": "GitHub Copilot", "slug": "github-copilot", "tagline": "代码补全老牌王者",
        "description": "GitHub 出品，深度集成 VS Code / JetBrains，支持 Chat 与代码审查。",
        "developer": "GitHub / Microsoft", "launched_at": date(2021, 6, 29),
        "form_factor": "windows_app", "is_free": False, "pricing_info": "$10/月",
        "need_vpn": False, "support_cli": True, "support_api": True,
        "official_url": "https://github.com/features/copilot",
        "logo_url": "https://github.githubassets.com/favicons/favicon.svg",
        "overall_score": 9.0, "usability_score": 9.5, "effect_score": 9.0, "price_score": 7.5, "speed_score": 9.3,
        "categories": ["coding"], "audiences": ["developer"],
    },
    {
        "name": "Claude Code", "slug": "claude-code", "tagline": "命令行里的 AI 工程师",
        "description": "Anthropic 官方 CLI，可直接在终端里让 Claude 读写你的仓库、跑测试。",
        "developer": "Anthropic", "launched_at": date(2025, 2, 24),
        "form_factor": "cli", "is_free": False, "pricing_info": "Pro 20/Max 100$ 起",
        "need_vpn": True, "support_cli": True, "support_api": True,
        "official_url": "https://www.anthropic.com/claude-code",
        "logo_url": "https://claude.ai/favicon.ico",
        "overall_score": 9.1, "usability_score": 8.8, "effect_score": 9.5, "price_score": 7.5, "speed_score": 8.8,
        "categories": ["coding", "agent"], "audiences": ["developer"],
    },
    {
        "name": "通义灵码", "slug": "tongyi-lingma", "tagline": "阿里出品的国产 Copilot",
        "description": "对中文、Java/Python/Go 项目友好，国内直连，免费使用，支持 IDE 插件与 CLI。",
        "developer": "阿里云", "launched_at": date(2023, 10, 31),
        "form_factor": "windows_app", "is_free": True, "pricing_info": "免费",
        "need_vpn": False, "support_cli": True, "support_api": False,
        "official_url": "https://tongyi.aliyun.com/lingma",
        "logo_url": "https://img.alicdn.com/imgextra/i1/O1CN01Rp5cMJ1WpWgBvJEf6_!!6000000002837-2-tps-512-512.png",
        "overall_score": 8.4, "usability_score": 9.0, "effect_score": 8.2, "price_score": 10.0, "speed_score": 8.5,
        "categories": ["coding"], "audiences": ["developer"],
    },
    {
        "name": "v0", "slug": "v0", "tagline": "Vercel 出品的 UI 生成器",
        "description": "一句话生成 React + Tailwind 组件/页面，直接导入 Next.js 项目。",
        "developer": "Vercel", "launched_at": date(2023, 10, 24),
        "form_factor": "saas", "is_free": True, "pricing_info": "免费额度；Premium $20/月",
        "need_vpn": True, "support_cli": False, "support_api": False,
        "official_url": "https://v0.dev",
        "logo_url": "https://v0.dev/favicon.ico",
        "overall_score": 8.7, "usability_score": 9.3, "effect_score": 8.8, "price_score": 7.8, "speed_score": 9.0,
        "categories": ["coding", "design"], "audiences": ["developer", "designer"],
    },

    # ---------- 写作文案 ----------
    {
        "name": "秘塔写作猫", "slug": "mita-xiezuomao", "tagline": "中文写作纠错与润色",
        "description": "国内写作界的老牌工具，错别字、病句、风格润色、查重一体化。",
        "developer": "秘塔科技", "launched_at": date(2019, 6, 1),
        "form_factor": "saas", "is_free": True, "pricing_info": "基础免费；会员 29/月",
        "need_vpn": False, "support_cli": False, "support_api": True,
        "official_url": "https://xiezuocat.com",
        "logo_url": "https://xiezuocat.com/favicon.ico",
        "overall_score": 8.2, "usability_score": 9.0, "effect_score": 8.3, "price_score": 8.5, "speed_score": 9.0,
        "categories": ["writing"], "audiences": ["student", "beginner"],
    },
    {
        "name": "Notion AI", "slug": "notion-ai", "tagline": "嵌在笔记里的写作助手",
        "description": "在 Notion 文档里按空格召唤 AI，续写、翻译、总结、生成表格一键到位。",
        "developer": "Notion Labs", "launched_at": date(2023, 2, 22),
        "form_factor": "saas", "is_free": False, "pricing_info": "$10/人/月",
        "need_vpn": True, "support_cli": False, "support_api": False,
        "official_url": "https://www.notion.so/product/ai",
        "logo_url": "https://www.notion.so/images/favicon.ico",
        "overall_score": 8.3, "usability_score": 9.0, "effect_score": 8.2, "price_score": 7.5, "speed_score": 8.5,
        "categories": ["writing", "office"], "audiences": ["beginner", "designer"],
    },

    # ---------- AI 绘画 ----------
    {
        "name": "Midjourney", "slug": "midjourney", "tagline": "艺术感最强的文生图",
        "description": "在 Discord 上通过 /imagine 指令生成高质量图像，V6 写实与国风俱佳。",
        "developer": "Midjourney Inc.", "launched_at": date(2022, 7, 12),
        "form_factor": "saas", "is_free": False, "pricing_info": "$10/月 起",
        "need_vpn": True, "support_cli": False, "support_api": False,
        "official_url": "https://www.midjourney.com",
        "logo_url": "https://www.midjourney.com/favicon.ico",
        "overall_score": 9.1, "usability_score": 7.5, "effect_score": 9.7, "price_score": 7.0, "speed_score": 8.8,
        "categories": ["image", "design"], "audiences": ["designer", "creator"],
    },
    {
        "name": "Stable Diffusion", "slug": "stable-diffusion", "tagline": "开源本地跑图模型",
        "description": "开源文生图大模型，社区模型（LoRA、ControlNet）丰富，本地部署零成本。",
        "developer": "Stability AI", "launched_at": date(2022, 8, 22),
        "form_factor": "windows_app", "is_free": True, "pricing_info": "开源免费",
        "need_vpn": False, "support_cli": True, "support_api": True,
        "official_url": "https://stability.ai",
        "logo_url": "https://stability.ai/favicon.ico",
        "overall_score": 8.8, "usability_score": 6.5, "effect_score": 9.2, "price_score": 10.0, "speed_score": 8.0,
        "categories": ["image"], "audiences": ["developer", "designer"],
    },
    {
        "name": "即梦 Dreamina", "slug": "jimeng", "tagline": "字节出品的中文文生图",
        "description": "抖音同款画风，支持参考图、剧情视频生成，中文理解好。",
        "developer": "字节跳动", "launched_at": date(2024, 3, 25),
        "form_factor": "saas", "is_free": True, "pricing_info": "每日免费积分",
        "need_vpn": False, "support_cli": False, "support_api": False,
        "official_url": "https://jimeng.jianying.com",
        "logo_url": "https://lf-cdn.jimeng.com/obj/cn-general/favicon.ico",
        "overall_score": 8.4, "usability_score": 9.0, "effect_score": 8.5, "price_score": 9.0, "speed_score": 8.5,
        "categories": ["image", "video"], "audiences": ["creator", "beginner"],
    },
    {
        "name": "liblib 哩布哩布", "slug": "liblib", "tagline": "国内 SD 模型社区",
        "description": "海量中文社区 LoRA/Checkpoint 模型，在线出图与下载，二次元与国风特别强。",
        "developer": "哩布哩布", "launched_at": date(2023, 6, 1),
        "form_factor": "saas", "is_free": True, "pricing_info": "免费积分 + 会员",
        "need_vpn": False, "support_cli": False, "support_api": True,
        "official_url": "https://www.liblib.art",
        "logo_url": "https://liblibai-online.liblib.cloud/favicon.ico",
        "overall_score": 8.0, "usability_score": 8.3, "effect_score": 8.5, "price_score": 8.8, "speed_score": 8.0,
        "categories": ["image"], "audiences": ["designer", "creator"],
    },

    # ---------- AI 视频 ----------
    {
        "name": "Sora", "slug": "sora", "tagline": "OpenAI 的文生视频",
        "description": "分钟级高清视频生成，物理一致性行业领先；订阅制放开中。",
        "developer": "OpenAI", "launched_at": date(2024, 12, 9),
        "form_factor": "saas", "is_free": False, "pricing_info": "Plus 含基础额度；Pro $200/月",
        "need_vpn": True, "support_cli": False, "support_api": False,
        "official_url": "https://sora.com",
        "logo_url": "https://cdn.oaistatic.com/assets/favicon-eex17e9e.svg",
        "overall_score": 8.8, "usability_score": 8.0, "effect_score": 9.5, "price_score": 6.0, "speed_score": 7.5,
        "categories": ["video"], "audiences": ["creator", "designer"],
    },
    {
        "name": "可灵 Kling", "slug": "kling", "tagline": "快手出品的中文视频模型",
        "description": "中文首屈一指的文生/图生视频，支持运动笔刷、首尾帧控制。",
        "developer": "快手", "launched_at": date(2024, 6, 6),
        "form_factor": "saas", "is_free": True, "pricing_info": "每日免费额度；会员 66/月",
        "need_vpn": False, "support_cli": False, "support_api": True,
        "official_url": "https://kling.kuaishou.com",
        "logo_url": "https://s2-111386.kwimgs.com/bs2/mmu-kling/favicon.ico",
        "overall_score": 8.9, "usability_score": 9.0, "effect_score": 9.2, "price_score": 8.5, "speed_score": 8.0,
        "categories": ["video"], "audiences": ["creator"],
    },
    {
        "name": "剪映 AI", "slug": "jianying-ai", "tagline": "视频剪辑里的一键 AI",
        "description": "字幕、配音、数字人、文本成片一站式，对 UP 主最友好。",
        "developer": "字节跳动", "launched_at": date(2023, 8, 1),
        "form_factor": "windows_app", "is_free": True, "pricing_info": "基础免费；专业版订阅",
        "need_vpn": False, "support_cli": False, "support_api": False,
        "official_url": "https://www.capcut.cn",
        "logo_url": "https://lf16-capcut.faceueditor.com/obj/capcut-default-cn/favicon.ico",
        "overall_score": 8.6, "usability_score": 9.5, "effect_score": 8.5, "price_score": 9.0, "speed_score": 8.8,
        "categories": ["video", "audio"], "audiences": ["creator", "beginner"],
    },
    {
        "name": "Runway", "slug": "runway", "tagline": "海外视频 AI 老玩家",
        "description": "Gen-3 视频、抠像、换背景、风格迁移等创作套件齐全。",
        "developer": "Runway", "launched_at": date(2018, 1, 1),
        "form_factor": "saas", "is_free": True, "pricing_info": "免费试用；$15/月 起",
        "need_vpn": True, "support_cli": False, "support_api": True,
        "official_url": "https://runwayml.com",
        "logo_url": "https://runwayml.com/favicon.ico",
        "overall_score": 8.5, "usability_score": 8.0, "effect_score": 9.0, "price_score": 7.0, "speed_score": 8.0,
        "categories": ["video"], "audiences": ["creator", "designer"],
    },

    # ---------- 语音音乐 ----------
    {
        "name": "Suno", "slug": "suno", "tagline": "一句话生成整首歌",
        "description": "歌词 + 风格 → 3 分钟成品音乐，V4 支持人声克隆和歌曲续写。",
        "developer": "Suno Inc.", "launched_at": date(2023, 12, 20),
        "form_factor": "saas", "is_free": True, "pricing_info": "每日免费额度；Pro $10/月",
        "need_vpn": True, "support_cli": False, "support_api": False,
        "official_url": "https://suno.com",
        "logo_url": "https://suno.com/favicon.ico",
        "overall_score": 9.0, "usability_score": 9.5, "effect_score": 9.2, "price_score": 8.0, "speed_score": 9.0,
        "categories": ["audio"], "audiences": ["creator", "beginner"],
    },
    {
        "name": "海螺 AI", "slug": "hailuo", "tagline": "MiniMax 的语音/视频创作",
        "description": "中文语音合成逼真，支持情感、多音色；也有视频生成能力。",
        "developer": "MiniMax", "launched_at": date(2024, 2, 2),
        "form_factor": "saas", "is_free": True, "pricing_info": "网页端免费",
        "need_vpn": False, "support_cli": False, "support_api": True,
        "official_url": "https://hailuoai.com",
        "logo_url": "https://hailuoai.com/favicon.ico",
        "overall_score": 8.5, "usability_score": 9.0, "effect_score": 8.8, "price_score": 9.5, "speed_score": 8.5,
        "categories": ["audio", "video"], "audiences": ["creator", "beginner"],
    },

    # ---------- 设计 / 办公 ----------
    {
        "name": "Canva", "slug": "canva", "tagline": "人人能用的在线设计",
        "description": "海量模板 + AI 文生图/魔法设计，做 PPT、海报、社交图最省心。",
        "developer": "Canva", "launched_at": date(2013, 1, 1),
        "form_factor": "saas", "is_free": True, "pricing_info": "基础免费；Pro 129/月",
        "need_vpn": False, "support_cli": False, "support_api": True,
        "official_url": "https://www.canva.cn",
        "logo_url": "https://www.canva.cn/favicon.ico",
        "overall_score": 8.6, "usability_score": 9.7, "effect_score": 8.2, "price_score": 8.0, "speed_score": 9.0,
        "categories": ["design", "office"], "audiences": ["beginner", "designer", "student"],
    },
    {
        "name": "Gamma", "slug": "gamma", "tagline": "AI 生成 PPT / 网页",
        "description": "一句话生成演示文稿、文档、网页，风格干净现代。",
        "developer": "Gamma", "launched_at": date(2022, 12, 1),
        "form_factor": "saas", "is_free": True, "pricing_info": "免费 400 积分；Plus $8/月",
        "need_vpn": True, "support_cli": False, "support_api": False,
        "official_url": "https://gamma.app",
        "logo_url": "https://gamma.app/favicon.ico",
        "overall_score": 8.4, "usability_score": 9.5, "effect_score": 8.3, "price_score": 8.0, "speed_score": 9.0,
        "categories": ["office", "design"], "audiences": ["student", "beginner"],
    },
    {
        "name": "WPS AI", "slug": "wps-ai", "tagline": "国产办公里的 AI",
        "description": "集成在 WPS 文档/表格/演示中，写作、公式、表格摘要全部内嵌。",
        "developer": "金山办公", "launched_at": date(2023, 11, 16),
        "form_factor": "windows_app", "is_free": True, "pricing_info": "基础免费；会员 169/年",
        "need_vpn": False, "support_cli": False, "support_api": False,
        "official_url": "https://ai.wps.cn",
        "logo_url": "https://qnssl.kdocs.cn/favicon.ico",
        "overall_score": 8.0, "usability_score": 9.0, "effect_score": 7.8, "price_score": 9.0, "speed_score": 8.5,
        "categories": ["office"], "audiences": ["beginner", "senior"],
    },

    # ---------- AI 搜索 ----------
    {
        "name": "Perplexity", "slug": "perplexity", "tagline": "带引用的 AI 搜索",
        "description": "每条回答都给出链接来源，Pro 模式可用 GPT-4o/Claude，研究党最爱。",
        "developer": "Perplexity AI", "launched_at": date(2022, 12, 7),
        "form_factor": "saas", "is_free": True, "pricing_info": "免费；Pro $20/月",
        "need_vpn": True, "support_cli": False, "support_api": True,
        "official_url": "https://www.perplexity.ai",
        "logo_url": "https://www.perplexity.ai/favicon.ico",
        "overall_score": 9.0, "usability_score": 9.3, "effect_score": 9.2, "price_score": 7.5, "speed_score": 9.2,
        "categories": ["search"], "audiences": ["developer", "student"],
    },
    {
        "name": "秘塔 AI 搜索", "slug": "metaso", "tagline": "中文无广告 AI 搜索",
        "description": "中文体验流畅、无广告，会自动生成思维导图与大纲，研究写作利器。",
        "developer": "秘塔科技", "launched_at": date(2024, 4, 1),
        "form_factor": "saas", "is_free": True, "pricing_info": "完全免费",
        "need_vpn": False, "support_cli": False, "support_api": False,
        "official_url": "https://metaso.cn",
        "logo_url": "https://metaso.cn/favicon.ico",
        "overall_score": 8.9, "usability_score": 9.5, "effect_score": 9.0, "price_score": 10.0, "speed_score": 9.0,
        "categories": ["search", "learning"], "audiences": ["student", "beginner"],
    },

    # ---------- 智能体 / Agent ----------
    {
        "name": "Coze 扣子", "slug": "coze", "tagline": "零代码搭 Bot 平台",
        "description": "字节出品的 Agent 搭建平台，插件丰富，可一键发布到飞书、微信、网页。",
        "developer": "字节跳动", "launched_at": date(2024, 2, 1),
        "form_factor": "saas", "is_free": True, "pricing_info": "免费额度充足",
        "need_vpn": False, "support_cli": False, "support_api": True,
        "official_url": "https://www.coze.cn",
        "logo_url": "https://www.coze.cn/favicon.ico",
        "overall_score": 8.7, "usability_score": 9.3, "effect_score": 8.5, "price_score": 9.5, "speed_score": 8.5,
        "categories": ["agent"], "audiences": ["developer", "beginner"],
    },
    {
        "name": "Dify", "slug": "dify", "tagline": "开源 LLM 应用开发平台",
        "description": "可视化编排 Workflow / RAG，企业私有化部署首选。",
        "developer": "LangGenius", "launched_at": date(2023, 5, 1),
        "form_factor": "saas", "is_free": True, "pricing_info": "开源免费；云版订阅",
        "need_vpn": False, "support_cli": True, "support_api": True,
        "official_url": "https://dify.ai",
        "logo_url": "https://dify.ai/favicon.ico",
        "overall_score": 8.6, "usability_score": 8.5, "effect_score": 8.8, "price_score": 9.5, "speed_score": 8.5,
        "categories": ["agent"], "audiences": ["developer"],
    },

    # ---------- 翻译 / 学习 ----------
    {
        "name": "DeepL", "slug": "deepl", "tagline": "翻译质量的标杆",
        "description": "欧洲语言翻译质量公认优秀，对长句、术语处理自然。",
        "developer": "DeepL GmbH", "launched_at": date(2017, 8, 28),
        "form_factor": "saas", "is_free": True, "pricing_info": "免费 5000 字；Pro 69/月",
        "need_vpn": True, "support_cli": False, "support_api": True,
        "official_url": "https://www.deepl.com",
        "logo_url": "https://static.deepl.com/img/favicon/favicon_96.png",
        "overall_score": 8.8, "usability_score": 9.5, "effect_score": 9.2, "price_score": 7.5, "speed_score": 9.3,
        "categories": ["translate", "writing"], "audiences": ["student", "beginner"],
    },
]


def _upsert_category(db: Session, data: dict) -> Category:
    obj = db.query(Category).filter_by(slug=data["slug"]).one_or_none()
    if obj is None:
        obj = Category(**data)
        db.add(obj)
        db.flush()
    else:
        for k, v in data.items():
            setattr(obj, k, v)
    return obj


def _upsert_tool(db: Session, data: dict, cat_map: dict[str, int]) -> None:
    cats = data.pop("categories", [])
    auds = data.pop("audiences", [])

    for k in ("overall_score", "usability_score", "effect_score", "price_score", "speed_score"):
        if k in data and data[k] is not None:
            data[k] = Decimal(str(data[k]))

    tool = db.query(Tool).filter_by(slug=data["slug"]).one_or_none()
    if tool is None:
        tool = Tool(**data)
        db.add(tool)
        db.flush()
    else:
        for k, v in data.items():
            setattr(tool, k, v)
        db.flush()

    db.query(ToolCategory).filter_by(tool_id=tool.id).delete()
    for c in cats:
        cid = cat_map.get(c)
        if cid:
            db.add(ToolCategory(tool_id=tool.id, category_id=cid))

    db.query(ToolAudience).filter_by(tool_id=tool.id).delete()
    for a in auds:
        db.add(ToolAudience(tool_id=tool.id, audience=a))


def _seed_admin(db: Session) -> None:
    admin = db.query(User).filter_by(username="admin").one_or_none()
    if admin is None:
        db.add(
            User(
                username="admin",
                email="admin@trueai.local",
                password_hash=hash_password("admin123456"),
                is_admin=True,
                balance=0,
            )
        )


def run() -> None:
    db: Session = SessionLocal()
    try:
        cat_map: dict[str, int] = {}
        for c in CATEGORIES:
            obj = _upsert_category(db, dict(c))
            cat_map[obj.slug] = obj.id
        db.commit()

        for t in TOOLS:
            _upsert_tool(db, dict(t), cat_map)
        db.commit()

        _seed_admin(db)
        db.commit()

        total = db.query(Tool).count()
        print(f"[seed] categories={len(CATEGORIES)}, tools inserted/updated={len(TOOLS)}, total tools in db={total}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
