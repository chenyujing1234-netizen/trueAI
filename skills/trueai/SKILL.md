---
name: trueai
description: Find the right AI SaaS app for any task using the TrueAI catalog (1,600+ curated apps with categories, sub-scores, pricing and real user reviews). Use whenever the user is choosing an AI tool, comparing AI products, looking up an app by name or URL, or wants pricing / features / reviews of a specific AI app.
version: 1.0.0
keywords: [ai-tools, ai-discovery, recommendation, saas, agent, trueai]
---

# TrueAI Skill

Helps an agent (Claude / Cursor / Cline / ChatGPT / your own pipeline)
recommend, look up and compare AI SaaS apps from the **TrueAI 真选AI**
catalog without ever leaving the chat.

The catalog ships with rich structured fields documented in
[`ai_tool_schema.json`](../../docs/ai_tool_schema.json) — `name`, `slug`,
`tagline`, `description`, `developer`, `form_factor`, `is_free`,
`pricing_info`, five sub-scores (`overall / usability / effect / price /
speed`), `official_url`, `categories`, `audiences`, optional
`external_reviews`, etc.

---

## When to use this skill

Trigger it any time the user is doing one of the following:

1. **Asking for a recommendation by need.** _"我想做一份中文 PPT"_, _"need
   a free AI to clean up my photos"_, _"我刚开始学编程，要免费的 AI 工具"_.
2. **Asking about a specific app by name.** _"Cursor 的定价是多少？"_,
   _"通义千问支持 API 吗？"_, _"What is Genspark?"_.
3. **Asking about an app by URL.** The user pastes `https://cursor.com`
   and wants to know what it is.
4. **Browsing / comparing inside a category.** _"Top 5 free AI coding
   tools"_, _"列几个国内能直接用的图像生成工具"_.

Do **not** use this skill for non-AI products, general web search, news,
or anything that doesn't map onto the TrueAI catalog.

---

## Setup (one-time)

The skill talks to a running TrueAI backend. Pick a base URL:

```bash
# Public hosted endpoint (recommended — nothing to install):
export TRUEAI_API_BASE=https://www.shiflowai.cloud

# Local dev (if you're running the TrueAI repo yourself):
# export TRUEAI_API_BASE=http://localhost:8000
```

There are two equivalent ways to invoke the skill — pick whichever your
agent supports best.

### A. Native MCP (recommended if your agent speaks MCP)

The TrueAI backend exposes two MCP transports — pick whichever your
client supports:

| Transport            | URL                                                      | When to use                                                |
| -------------------- | -------------------------------------------------------- | ---------------------------------------------------------- |
| **Streamable HTTP** (recommended) | `https://www.shiflowai.cloud/mcp`           | Smithery, modern Claude Desktop / Cursor / Cline / Windsurf |
| SSE (legacy)         | `https://www.shiflowai.cloud/mcp-sse/sse`                | Older MCP clients that haven't migrated yet                |

In **Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`),
**Cursor** (`~/.cursor/mcp.json`), **Cline**, **Continue**, **Windsurf**:

```json
{
  "mcpServers": {
    "trueai": {
      "url": "https://www.shiflowai.cloud/mcp"
    }
  }
}
```

(For local dev replace the URL with `http://localhost:8000/mcp`.)

You'll then see four tools available to the agent:

| Tool                | Purpose                                                   |
| ------------------- | --------------------------------------------------------- |
| `recommend_ai_tools(description, top_k)` | Need description → ranked apps    |
| `get_ai_tool(name_or_url, include_reviews)` | Name / slug / URL → full record |
| `list_ai_tools(category, free_only, form_factor, sort, page, page_size)` | Browse |
| `list_categories()` | Discover category slugs                                   |

### B. Plain HTTP (works with any agent, no MCP needed)

The same data is also reachable via the REST API. Any agent that can run
shell commands or do HTTP calls can use it directly.

All URLs below assume `TRUEAI_API_BASE=https://www.shiflowai.cloud`.

| Capability              | HTTP call |
| ----------------------- | --------- |
| Recommend by need       | `GET  https://www.shiflowai.cloud/api/search/chat?q=<urlencoded description>` |
| Get app by id or slug   | `GET  https://www.shiflowai.cloud/api/tools/{id_or_slug}` |
| Browse with filters     | `GET  https://www.shiflowai.cloud/api/tools?category=coding&free=true&sort=overall&page=1&page_size=20` |
| External reviews of app | `GET  https://www.shiflowai.cloud/api/tools/{id_or_slug}/external-reviews?page=1&page_size=10` |
| List categories         | `GET  https://www.shiflowai.cloud/api/categories` |
| Compare 2–3 apps        | `POST https://www.shiflowai.cloud/api/tools/compare`  body: `[id1, id2, id3]` |

All responses are JSON. Schema: see [`docs/ai_tool_schema.json`](../../docs/ai_tool_schema.json).

---

## Recipes for the agent

### Recipe 1 — User describes a need → recommend tools

```bash
curl -sG "$TRUEAI_API_BASE/api/search/chat" \
     --data-urlencode "q=我是新手想做小红书封面，要免费的 AI"
```

Response shape:

```jsonc
{
  "intents":    { "categories": ["image","design"], "audiences": ["beginner"], "free": true, "no_vpn": false },
  "candidates": [ /* Tool briefs, already ranked by overall_score */ ],
  "external":   [ /* fallback nav sites only when candidates is empty */ ]
}
```

Present the top 3 candidates with a one-sentence rationale per item, then
link the `official_url`. If `candidates` is empty, surface the `external`
nav sites as a fallback rather than apologizing.

### Recipe 2 — User names a specific app

```bash
# By slug (preferred, exact)
curl -s "$TRUEAI_API_BASE/api/tools/cursor"

# By name — fall back to fuzzy search and take the top hit
curl -sG "$TRUEAI_API_BASE/api/tools" --data-urlencode "q=通义千问" \
  | jq '.items[0].slug' \
  | xargs -I{} curl -s "$TRUEAI_API_BASE/api/tools/{}"
```

### Recipe 3 — User pastes a URL

```bash
# Extract the brand keyword from the host (cursor.com → cursor) and search
HOST=$(echo "https://cursor.com" | awk -F/ '{print $3}' | sed 's/^www\.//')
BRAND=$(echo "$HOST" | awk -F. '{print $(NF-1)}')
curl -sG "$TRUEAI_API_BASE/api/tools" --data-urlencode "q=$BRAND" \
  | jq -r '.items[] | select(.official_url and (.official_url | contains("'"$HOST"'"))) | .slug' \
  | head -1 \
  | xargs -I{} curl -s "$TRUEAI_API_BASE/api/tools/{}"
```

(Or just call `get_ai_tool` over MCP — it does the same resolution
internally.)

### Recipe 4 — Add real-user reviews for "usage tips"

```bash
curl -s "$TRUEAI_API_BASE/api/tools/cursor/external-reviews?page_size=5"
```

Surface 2–3 of the most upvoted reviews as quotes when the user asks
_"how do people actually use it?"_ or _"is it any good?"_.

### Recipe 5 — Compare a shortlist

```bash
curl -s -X POST "$TRUEAI_API_BASE/api/tools/compare" \
     -H "content-type: application/json" \
     -d '[9, 16, 23]'
```

Returns each tool's five sub-scores side by side — render as a markdown
table.

---

## Output guidelines for the agent

- **Always include `official_url`** when recommending — let the user click
  through.
- **Quote sub-scores honestly** (`overall_score / usability_score /
  effect_score / price_score / speed_score`, all 0–10). A `0` means
  "not yet rated", not "bad".
- **Respect `is_free`, `need_vpn` and `form_factor`** when the user has
  expressed a constraint about money, location or platform.
- **Don't fabricate fields**. If a field is missing from the JSON
  response, say so or just omit it.
- **Prefer 1–3 recommendations** when the user is undecided; offer to
  drill into any of them.

---

## Field reference (excerpt)

| Field           | Type      | Notes |
| --------------- | --------- | ----- |
| `name`          | string    | Brand-cased display name. |
| `slug`          | string    | URL-safe id, unique. |
| `tagline`       | string    | Short subtitle. |
| `form_factor`   | enum      | `saas` / `mobile` / `cli` / `windows_app` / `web` / `browser_extension` / `api`. |
| `is_free`       | bool      | True if any free tier exists. |
| `need_vpn`      | bool      | True if mainland-China users need a VPN. |
| `pricing_info`  | string    | Free-form pricing summary. |
| `overall_score` | 0–10      | Weighted from the four sub-scores. |
| `categories`    | string[]  | Category slugs. |
| `official_url`  | URL       | Vendor's homepage. |

Full schema (34 fields + nested `Category` / `ExternalReview`):
[`docs/ai_tool_schema.json`](../../docs/ai_tool_schema.json).

---

## License

MIT. See the TrueAI repository root.
