# domino-cline-plugin

Domino Data Lab platform knowledge — workspaces, jobs, model deployment,
experiment tracking, GenAI tracing, Spark/Ray/Dask, and app deployment — as
a native [Cline](https://cline.bot) skill pack, plus the Domino REST API MCP
server.

This is a separate, standalone tool from
[domino-claude-plugin](https://github.com/dominodatalab/domino-claude-plugin)
(the Claude Code plugin) because Cline and Claude Code are different products
with different extension mechanisms. The instructional *content* is sourced
from that repo and kept in sync via `scripts/sync_from_domino_claude_plugin.py`
— domino-claude-plugin remains the source of truth for skill authoring;
this repo just re-packages it for Cline.

> **Status: not yet ready to share.** Being tested locally before publishing.

## What's here

- `skills/` — 30 Cline-native skills (`SKILL.md` with `name:`/`description:`
  frontmatter). Cline auto-routes to these by description; no manual
  invocation needed. Includes:
  - 23 platform skills (deploying apps, jobs, experiment tracking, etc.)
  - 3 skills adapted from domino-claude-plugin's specialized agents
    (domino-debug, domino-deploy, domino-setup) — Cline has no sub-agent
    spawning mechanism, so these are auto-routed/slash-invokable skills
    rather than isolated agent contexts
  - 4 skills adapted from domino-claude-plugin's slash commands
    (domino-app-init, domino-debug-proxy, domino-experiment-setup,
    domino-trace-setup) — also usable as literal `/domino-app-init` etc.
    slash commands in Cline
- `mcp-servers/domino_mcp_server/` — MCP server wrapping the Domino REST API
  (run jobs, check status, sync files to DFS projects). Copied as-is; not
  Cline-specific.

Not carried over from domino-claude-plugin, deliberately:
- `mcp-servers/skills_mcp_server/` — built as a workaround for clients
  without native skill-routing (e.g. Continue+Qwen). Redundant here since
  Cline routes skills natively.
- `hooks/`, `output-styles/` — no Cline equivalent exists today.

## Install

**Skills** (global, applies across all your projects):

```bash
for d in skills/*/; do
  name=$(basename "$d")
  ln -sfn "$(pwd)/$d" ~/.cline/skills/"$name"
done
```

**MCP server** (Domino REST API access) — add via Cline's MCP settings UI:

```json
{
  "mcpServers": {
    "domino_server": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/domino-cline-plugin/mcp-servers/domino_mcp_server", "run", "domino_mcp_server.py"]
    }
  }
}
```

Then set `DOMINO_API_KEY` and `DOMINO_HOST` in
`mcp-servers/domino_mcp_server/.env` (gitignored).

## Keeping in sync with domino-claude-plugin

```bash
python3 scripts/sync_from_domino_claude_plugin.py [--source /path/to/domino-claude-plugin]
```

Defaults to a sibling checkout (`../domino-claude-plugin`). Re-copies all
skills/agents/commands, records the synced source commit in
`.sync-source.json`, and preserves your local `.env` if one already exists.
Review with `git diff` before committing — some upstream skills carry known
content issues (placeholder auth/hosts) tracked in domino-claude-plugin's own
`SKILL_AUDIT.md`.

## Known content caveats

Per domino-claude-plugin's `SKILL_AUDIT.md`, several skills still contain
placeholder auth (`X-Domino-Api-Key` + hardcoded key) or placeholder hosts
(`your-domino.com`). Prefer `$DOMINO_API_HOST` and the workspace bearer-token
pattern, and verify endpoints against the live swagger before trusting a
skill's example verbatim. This will improve as those audit items get fixed
upstream and pulled in via the next sync.

## License

MIT — see [LICENSE](./LICENSE). Content originates from domino-claude-plugin
(also MIT, Domino Data Lab).
