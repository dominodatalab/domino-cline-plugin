# domino-cline-plugin

Domino Data Lab platform knowledge — workspaces, jobs, model deployment,
experiment tracking, GenAI tracing, Spark/Ray/Dask, and app deployment — as
a native [Cline](https://cline.bot) skill pack, plus the Domino REST API MCP
server.

> **Status: not yet ready to share.** Being tested locally before publishing.

## What's here

- `skills/` — 31 Cline-native skills (`SKILL.md` with `name:`/`description:`
  frontmatter). Cline auto-routes to these by description; no manual
  invocation needed. Includes:
  - 23 platform skills (deploying apps, jobs, experiment tracking, etc.)
  - 3 skills adapted from specialized agents (domino-debug, domino-deploy,
    domino-setup) — Cline has no sub-agent spawning mechanism, so these are
    auto-routed/slash-invokable skills rather than isolated agent contexts
  - 4 skills adapted from slash commands (domino-app-init,
    domino-debug-proxy, domino-experiment-setup, domino-trace-setup) — also
    usable as literal `/domino-app-init` etc. slash commands in Cline
  - 4 platform-ops/reference skills:
    - `domino-teleport` — Teleport (`tsh`/`tsh7`) login + kubectl access to
      Domino's Kubernetes clusters, keyed by the same cluster aliases as
      `~/.domino/.env`'s `DOMINO_CLUSTERS`
    - `domino-access` — standard access-check protocol (REST API → Teleport →
      AWS, in that order) with re-auth prompts when a credential/session
      expires
    - `aws-ops` — AWS CLI ops (S3, EFS, EKS, CloudWatch Logs) against
      Domino's infra. Deliberately self-extending: its own instructions
      tell Cline to append a new section documenting any AWS service it
      handles that isn't yet covered, so the file grows with use instead
      of staying frozen at what it shipped with.
    - `domino-docs` — explicit lookups against `docs.dominodatalab.com` for
      conceptual/product questions, version-matched to the target cluster
      via `domino-teleport`'s registry. Complements (doesn't replace) the
      standing "verify against the live swagger/docs before implementing"
      behavior in the global Cline rule — see "Docs & swagger" below.
- `mcp-servers/domino_mcp_server/` — MCP server wrapping the Domino REST API
  (run jobs, check status, sync files to DFS projects, check cluster access).
- `hooks/PostToolUse` — a single PostToolUse hook (app.sh binds to `0.0.0.0`,
  Python syntax check, `black` formatting, `hadolint` on Dockerfiles). See
  "Hooks" below for why this isn't split per-tool.
- `CONTRIBUTING.md` — authoring guidance and the Skill Authoring Standards.
- `SKILL_AUDIT.md` — tracking checklist of known skill content issues.

Not included, deliberately:
- `mcp-servers/skills_mcp_server/` — a workaround for clients without native
  skill-routing (e.g. Continue+Qwen). Redundant here since Cline routes
  skills natively.
- `output-styles/` — see "Known gaps" below.

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

Then fill in `~/.domino/.env` (next to your existing Domino CLI data). It supports
either a single Domino instance (`DOMINO_API_KEY`/`DOMINO_HOST`) or several
(`DOMINO_CLUSTERS=alias1,alias2` + per-alias `DOMINO_HOST_<ALIAS>`/
`DOMINO_API_KEY_<ALIAS>`) — see the comments in that file. Every
domino_server tool takes an optional `cluster` argument matching one of
those aliases; a `list_domino_clusters` tool reports what's configured, and
the global Cline rule (`~/Documents/Cline/Rules/domino.md`) tells Cline to
call it before assuming which instance to target when more than one is
set up.

## Hooks

Cline's hook mechanism is architecturally different from Claude Code's
`hooks.json`: it runs exactly **one executable file per event**, named after
the event (`PreToolUse`, `PostToolUse`, `SessionStart`, `UserPromptSubmit`,
`PreCompact`, `PostToolUseFailure`, `PostToolBatch`) — no per-tool `matcher`
config. Verified directly against the installed extension's code
(`saoudrizwan.claude-dev`); Cline's own hooks docs page just redirects to an
undocumented "SDK Plugins" page.

The four example hooks (a `PreToolUse` check on Write for app.sh, and three
`PostToolUse` checks on Edit/Write) are combined into the single
`hooks/PostToolUse` script here, rather than split into `PreToolUse` +
`PostToolUse`. Reason: the app.sh check needs to inspect file content, and
whether `PreToolUse` gives reliable access to *pending* write content (before
it lands on disk) couldn't be confirmed from the extension code —
`PostToolUse` reads the already-written file from disk instead, which is
unambiguous. Always exits 0 (never blocks).

Install: `ln -sfn "$(pwd)/hooks/PostToolUse" ~/Documents/Cline/Hooks/PostToolUse`
(global) or copy to `.clinerules/hooks/PostToolUse` per-project.

## Docs & swagger

Two mechanisms, deliberately not one, so "check the docs" doesn't depend on
the model deciding a particular question needs it:

1. **Standing behavior, via the global Cline rule** (`~/Documents/Cline/Rules/domino.md`,
   not part of this repo): before implementing or debugging real work
   against a Domino cluster, resolve the host via `list_domino_clusters`
   and check the live swagger, and for platform-behavior questions, check
   `docs.dominodatalab.com` — regardless of which skill triggered the work.
   This is the fix for the actual failure mode: assumption-driven debug
   loops that a 10-second doc check would've avoided. It's an instruction,
   not an enforced check.
2. **`domino-docs` skill** — for explicit, on-demand conceptual lookups
   ("how does X work in Domino") independent of any specific task.

Several skills (`domino-apps`, `domino-jobs`, `domino-python-sdk`,
`domino-ai-gateway`, `domino-ui-design`) had a swagger-fetch snippet using
`$DOMINO_API_HOST` — which is only set **inside** a Domino
workspace/job/app. Cline runs from the laptop, where that env var doesn't
exist; those snippets have been fixed to resolve the host via
`list_domino_clusters` instead, with the in-workspace form kept as an
alternative. `domino-governance` didn't need this — it already derives its
API base from the JWT `iss` claim, which works in either context.

## Known gaps

**Output styles — not implemented, by decision (2026-08-26).** Claude
Code's `output-styles/domino-learning.md` and `domino-mlops.md` have no
Cline equivalent: confirmed via Cline's docs index (`llms.txt`, zero hits
for "output style"/"persona"/"tone") and a grep of the installed extension
code (zero genuine matches). Cline has no swappable-persona/system-prompt
mechanism.

Both source files set `keep-coding-instructions: true`, meaning neither
changes how tasks actually get solved — they only append a required
formatted block after each task (`domino-learning`: a "Domino Insight"
explainer; `domino-mlops`: an "MLOps Checklist" plus proactively suggesting
things like dataset snapshots or model monitoring). Since that's just
injected instruction text, not a real mode-switch, the best available
approximation is a manually-toggled global Cline Rule (Cline's Rules panel
supports enabling/disabling individual rules) — that would faithfully
reproduce the actual content, just without the one-click "switch modes"
UX. Decided to skip for now; revisit if the always-on-until-toggled
workflow turns out to matter in practice.

## Known content caveats

Several skills may still reference endpoint paths that haven't been verified
against the current Domino API. The static violations (placeholder auth,
placeholder hosts, `python-domino` SDK examples) have been resolved — see
`SKILL_AUDIT.md`. For Rules 4 (verified endpoints) and 5 (smoke-tested
payloads), verify per-PR. Prefer the workspace bearer-token pattern (when
running inside a workspace) or `list_domino_clusters` (when running from
Cline on the laptop) over a skill's example verbatim, and verify endpoints
against the live swagger either way — see "Docs & swagger" above.

## Testing

The test suite (`pytest`) enforces the Skill Authoring Standards statically
across all `skills/*/*.md` files and functionally tests the MCP server's
credential loading + `check_domino_api_access` tool.

```bash
scripts/test.sh            # from the repo root
# or, from anywhere on your Mac (any cwd), by absolute path:
/Users/michaelsnyder/repos/domino-cline-plugin/scripts/test.sh
# or, from the repo root, without the wrapper:
./mcp-servers/domino_mcp_server/.venv/bin/python -m pytest
```

> **Why `scripts/test.sh`?** pytest only honors the `testpaths` ini option
> when invoked from the directory that contains `pytest.ini` (the repo root).
> If you run bare `pytest` from a subdirectory (e.g. inside
> `mcp-servers/domino_mcp_server/`), it silently collects 0 tests. The wrapper
> avoids that footgun.

## License

MIT — see [LICENSE](./LICENSE). Content is derived from Domino Data Lab
materials (also MIT, Domino Data Lab).
