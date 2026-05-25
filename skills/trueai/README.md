# TrueAI Skill

A single-file **agent skill** that lets any LLM agent (Claude, Cursor,
Cline, Continue, Windsurf, ChatGPT, custom LangChain / LlamaIndex, …)
recommend, look up and compare AI SaaS apps using the
[TrueAI 真选AI](../../) catalog.

## Two equivalent ways to use it

| Form               | What it is                                                                 | Where you put it |
| ------------------ | -------------------------------------------------------------------------- | ---------------- |
| **`SKILL.md`**     | One markdown file describing when & how to call the TrueAI HTTP API.       | Drop into your agent's skill / prompt-context directory. Works with any agent (no special protocol). |
| **Embedded MCP**   | Same skill exposed as MCP tools from the running TrueAI backend at `/mcp/sse`. | Point any MCP-compatible host at the URL — no extra process or venv. |

Both forms hit the **same** TrueAI backend HTTP API. There is no separate
service to install or maintain.

## Quick start

You don't need to run anything locally — the catalog is hosted at
**`https://www.shiflowai.cloud`**. Pick one of the two forms below.

### Form A — drop the SKILL.md into your agent

```bash
# Example for Cursor (per-project skill)
mkdir -p .cursor/skills
cp skills/trueai/SKILL.md .cursor/skills/trueai.md
```

Or for any Anthropic Skills-compatible runtime, copy the entire
`skills/trueai/` folder into your skills root.

### Form B — connect over MCP

Add this to **Claude Desktop** / **Cursor** / **Cline** / **Continue** /
**Windsurf** config:

```json
{
  "mcpServers": {
    "trueai": { "url": "https://www.shiflowai.cloud/mcp/sse" }
  }
}
```

You'll get four tools: `recommend_ai_tools`, `get_ai_tool`,
`list_ai_tools`, `list_categories`.

> Running TrueAI yourself? Replace the URL with `http://localhost:8000/mcp/sse`.

## Files

```
skills/trueai/
├── README.md                  ← this file
├── SKILL.md                   ← the skill itself (drop into your agent)
└── examples/
    ├── claude_desktop.json    ← MCP host config snippet
    └── cursor_mcp.json
```

The backing MCP server lives in
[`backend/app/api/mcp_server.py`](../../backend/app/api/mcp_server.py) and
is mounted at `/mcp` by [`backend/app/main.py`](../../backend/app/main.py).
It runs inside the same uvicorn process as the REST API — no extra venv,
no daemon to babysit.

## License

MIT.
