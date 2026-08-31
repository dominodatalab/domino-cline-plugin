---
paths:
  - "**/*"
---

# Domino platform work

Domino skills (domino-apps, domino-jobs, domino-data-sdk, etc.) are installed
globally under `~/.cline/skills/` as symlinks into
`/absolute/path/to/domino-cline-plugin` (this plugin, wherever you cloned it).
They auto-load when relevant — no action needed to invoke them.

Things to know when one fires:

1. **Known unverified content**: per `SKILL_AUDIT.md`, a handful of skills may
   still contain unverified endpoint paths or payloads left over from
   drafting. Prefer the workspace bearer-token pattern (`GET
   localhost:8899/access-token` → `Authorization: Bearer $TOKEN`) and
   `$DOMINO_API_HOST` over anything a skill shows verbatim **when actually
   running inside a Domino workspace/job/app**. From Cline on the laptop,
   that env var isn't set; see the next point instead.

1a. **Verify before implementing or debugging, don't assume** — this
    applies whenever a domino-* skill is doing real work against a Domino
    cluster, not just when a skill happens to mention it:
    - **API shape/endpoints**: resolve the target cluster's host via
      `list_domino_clusters` (don't rely on `$DOMINO_API_HOST` from
      Cline — that's workspace-only), then `web_fetch` `<host>/assets/public-api.json`
      (the live swagger) before trusting a skill's inline curl/code example.
      The swagger is the source of truth, not the skill text.
    - **Platform behavior/concepts** beyond the raw API surface (what a
      setting does, how a feature is supposed to work): `web_fetch` the
      relevant page on `docs.dominodatalab.com`. It's versioned (Cloud/current,
      6.2, 6.1, ...) — match the version to the target cluster's
      `domino_version` from the `domino-teleport` registry rather than
      always assuming "latest," since behavior genuinely differs across
      versions.
    - **Internal engineering/ops docs** (Fleetcommand, Teleport setup,
      other ENG-space how-tos — not customer-facing product behavior): if
      you have a Confluence/Atlassian MCP server configured, use it —
      `dominodatalab.atlassian.net/wiki`. This is optional and not something
      this plugin sets up; see the README's "Optional: Atlassian/Confluence
      MCP" section if you want it.
    - This is an instruction, not an enforced check — it shapes behavior,
      it doesn't guarantee it. If Cline seems to be debugging from
      assumptions instead of checking one of the above, that's worth
      calling out directly rather than letting the loop continue.

2. **The `domino_server` MCP tool** (if connected) needs credentials in
   `~/.domino/.env` to reach the Domino API from outside a workspace (legacy
   fallback: `mcp-servers/domino_mcp_server/.env` in the plugin repo). If a
   domino_server tool call fails with a missing-credential error, that's the
   file to check — don't invent or guess a key/host.

   You may have **more than one Domino instance configured**
   (`DOMINO_CLUSTERS=alias1,alias2,...`), each with its own host/API key.
   Every domino_server tool takes an optional `cluster` argument matching
   one of those aliases.
   - Before the first domino_server call in a session, or whenever which
     instance is ambiguous, call `list_domino_clusters` to see what's
     configured — don't assume there's only one.
   - If more than one cluster is configured and the request doesn't
     make the target instance obvious, ask which cluster/alias to use
     rather than defaulting silently — a job run or file sync against the
     wrong Domino instance isn't something to guess at.
   - If a project, host, or alias is named that maps clearly to one
     configured cluster, pass that `cluster` explicitly rather than
     omitting it.

3. **Access-check protocol** — when asked "do you have access to this
   cluster" (or to verify reachability/connectivity), run all three legs in
   this order of precedence and report each one's status:
   1. **REST API** — call `list_domino_clusters`, then
      `check_domino_api_access(cluster=<alias>)`.
   2. **Teleport/kubectl** — `tsh status`, then `tsh kube ls` (see the
      `domino-teleport` skill for proxy/version mapping and the registry).
   3. **AWS** — `aws sts get-caller-identity` (see the `aws-ops` skill).
   If any leg fails with an authentication or expiry error (401/403, expired
   token, expired session), prompt for re-auth on **that specific path**
   — regenerate the API key and update `~/.domino/.env`, run
   `tsh login` (+ `tsh kube login`), or run `okta-aws` — before assuming
   anything else is wrong.
