# Publishing the TrueAI MCP / Skill

This page tracks where TrueAI is listed and what to do (or copy-paste)
when registering on a new MCP / agent-tool directory.

The server lives at:

* SSE endpoint:  `https://www.shiflowai.cloud/mcp/sse`
* GitHub repo:   `https://github.com/chenyujing1234-netizen/trueAI`
* Hosted demo:   `https://www.shiflowai.cloud`

---

## 1. Smithery.ai  (largest MCP marketplace)

1. Sign in at <https://smithery.ai> with GitHub.
2. **Add Server → Connect GitHub repository** → pick
   `chenyujing1234-netizen/trueAI`.
3. Smithery reads [`smithery.yaml`](../../smithery.yaml) at the repo root
   and lists the server automatically. No build required (remote SSE).
4. Add tags: `ai-tools`, `recommendation`, `directory`.
5. Listed at `https://smithery.ai/server/@chenyujing1234-netizen/trueai`.

---

## 2. Anthropic MCP Registry  (official)

The official registry uses a per-server manifest. Ours is at
[`server.json`](../../server.json) (repo root).

**Publishing** (one-time per release):

```bash
# Install the official publisher (Go binary)
brew install mcp-publisher        # macOS
# or:  go install github.com/modelcontextprotocol/registry/cmd/mcp-publisher@latest

# In the repo root:
cd ~/path/to/trueAI
mcp-publisher login github        # opens GitHub OAuth
mcp-publisher publish             # reads ./server.json
```

After this the server appears at
<https://registry.modelcontextprotocol.io/v0/servers?search=trueai>
and is consumable by every MCP client that uses the registry.

The registry verifies ownership via the `io.github.<user>/<repo>` naming
convention, which is why our `name` is
`io.github.chenyujing1234-netizen/trueai`.

---

## 3. awesome-mcp-servers  (community list, ~60k stars)

Submit a one-line PR to <https://github.com/punkpeye/awesome-mcp-servers>.

Add this entry under **🎨 Discovery & Search** (or the closest section):

```markdown
- [TrueAI](https://github.com/chenyujing1234-netizen/trueAI) - Find the right
  AI SaaS app for any task: search 1,600+ curated apps by need, name, or URL,
  with categories, ratings and real user reviews. Hosted MCP at
  `https://www.shiflowai.cloud/mcp/sse`.
```

Suggested PR title: `Add TrueAI - 1,600+ AI tools catalog (hosted MCP)`.

---

## 4. PulseMCP  (directory + uptime monitor)

1. Visit <https://www.pulsemcp.com/submit>.
2. Server name: `TrueAI`
3. SSE URL: `https://www.shiflowai.cloud/mcp/sse`
4. GitHub: `https://github.com/chenyujing1234-netizen/trueAI`
5. Description: copy from `server.json`.

---

## 5. Cursor Directory  (Cursor user community)

1. Visit <https://cursor.directory/mcp/submit> (or `https://cursor.directory/submit`).
2. Pick category **MCP Server**.
3. Paste the URL `https://www.shiflowai.cloud/mcp/sse` and the GitHub link.

---

## 6. Product Hunt  (general visibility)

Recommend a coordinated launch (Sunday night → Monday morning PT). Headline
ideas:

* "TrueAI — your agent's brain for picking the right AI tool"
* "TrueAI Skill / MCP — 1,600+ AI apps your AI can finally evaluate"

Attach: short demo video of Claude / Cursor using `recommend_ai_tools` to
suggest an app.

---

## Stand-up copy-paste for any other directory

| Field        | Value |
|--------------|-------|
| Name         | TrueAI |
| Tagline      | Find the right AI SaaS app for any task |
| Description  | 1,600+ curated AI SaaS apps with categories, sub-scores, pricing and real user reviews. Exposes 4 MCP tools so agents can recommend, look up and compare AI tools. |
| Website      | https://www.shiflowai.cloud |
| Repository   | https://github.com/chenyujing1234-netizen/trueAI |
| MCP endpoint | https://www.shiflowai.cloud/mcp/sse (SSE transport) |
| Skill file   | https://github.com/chenyujing1234-netizen/trueAI/blob/main/skills/trueai/SKILL.md |
| Schema       | https://github.com/chenyujing1234-netizen/trueAI/blob/main/docs/ai_tool_schema.json |
| License      | MIT |
| Tags         | ai-tools, mcp, agent, recommendation, directory, catalog |
