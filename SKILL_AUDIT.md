# Skill Audit — Compliance with Skill Authoring Standards

Regenerated for **domino-cline-plugin** (Cline) against the rules in
[CONTRIBUTING.md](./CONTRIBUTING.md#skill-authoring-standards).

This is a tracking checklist — it captures the work to be done, not fixes
landed here. Rules 4 (verified endpoints) and 5 (smoke-tested payloads) are
not statically auditable and must be verified per-PR; this file tracks the
static rules (1–3, 7) plus the SDK-reference and CI/CD exceptions.

> **Note on provenance:** an earlier `SKILL_AUDIT.md` was copied verbatim from
> the Claude Code plugin (`domino-claude-plugin`) and referenced that repo's
> skill paths (`skills/jobs`, `skills/environments`, …). Those paths do not
> exist here — this repo prefixes skill directories with `domino-`. That copy
> was also dated 2026-05-08 and listed violations that have since been fixed
> (e.g. `jobs` and `launchers` auth violations). This file was regenerated
> with correct paths and line numbers on 2026-08-27, then found on
> **2026-08-31** (via an adversarial review) to have several false "0
> violations" claims of its own — see the 2026-08-31 notes under Rules 3 and
> 7 below. Take "0 skills affected" claims in any snapshot of this file with
> proportionate skepticism; static audits only catch what their grep pattern
> covers.
>
> Also on 2026-08-31: `domino-app-init`, `domino-debug-proxy`,
> `domino-experiment-setup`, and `domino-trace-setup` moved out of `skills/`
> entirely, into `workflows/` — they were ported from upstream Claude Code
> slash commands but shipped with `/command`-shaped bodies that don't match
> how Cline skills actually trigger (auto-routed from description, not
> typed). Cline Workflows are the correct native equivalent of a slash
> command. They're no longer subject to this audit's skill-focused rules in
> the same way, though their Domino API examples still follow the same
> auth/host/SDK conventions.

## Clean skills (23)

No static violations (rules 1–3, 7) in their `SKILL.md`:

- `skills/aws-ops/SKILL.md`
- `skills/domino-access/SKILL.md`
- `skills/domino-data-connectivity/SKILL.md`
- `skills/domino-debug/SKILL.md`
- `skills/domino-deploy/SKILL.md`
- `skills/domino-docs/SKILL.md`
- `skills/domino-environments/SKILL.md`
- `skills/domino-experiment-tracking/SKILL.md`
- `skills/domino-flows/SKILL.md`
- `skills/domino-genai-tracing/SKILL.md`
- `skills/domino-governance/SKILL.md`
- `skills/domino-jobs/SKILL.md` — see Rule 3 note below; the actual violation was in this file's body, not `SKILL.md`'s frontmatter-adjacent examples, and is now fixed.
- `skills/domino-model-monitoring/SKILL.md`
- `skills/domino-modeling-assistant/SKILL.md`
- `skills/domino-projects/SKILL.md`
- `skills/domino-setup/SKILL.md`
- `skills/domino-teleport/SKILL.md`
- `skills/domino-ui-bootstrap/SKILL.md`
- `skills/domino-ui-design/SKILL.md`
- `skills/domino-workspaces/SKILL.md`
- `skills/netapp-volumes/SKILL.md`
- `skills/tags-and-properties/SKILL.md`
- `skills/domino-governance/SKILL.md` (derives API base from the JWT `iss` claim — exempt from Rule 7 by construction, not by omission)

`domino-debug`, `domino-deploy`, `domino-setup` had their Claude Code
sub-agent frontmatter (`tools:`/`model:`/`skills:`) dropped on 2026-08-31 —
not a Rule 1–3/7 violation, but worth noting since it's the same class of
fix as the workflows move above (Cline-standalone-ness, not auth/host/SDK).

## Violations by skill

Each item links to the rule it violates and the offending line(s). Check the
box when fixed and the corresponding line(s) verified against the live API.

### Rule 1 — Authenticate with the local token endpoint, not API keys

`DOMINO_USER_API_KEY` / `X-Domino-Api-Key` remaining as *examples*:

- [x] `skills/domino-data-sdk/SKILL.md:179` — replaced with `DOMINO_TOKEN_FILE` (preferred, short-lived).
- [x] `skills/domino-python-sdk/SKILL.md:80` — deprecated Options 1 & 2 removed; only the inside-Domino auto-configure path remains.
- [x] `skills/domino-python-sdk/SKILL.md:72,79` — deprecated host + API-key examples removed (same block).

**Resolution (2026-08-27):** All deprecated API-key examples have been removed or
replaced. The SDK-reference skills now document only the preferred token-based
auth path (`DOMINO_TOKEN_FILE` for data SDK, inside-Domino auto-config for
python SDK). The `X-Domino-Api-Key` in `REACT-CICD.md:196` is the correct external
CI/CD REST header (no access-token sidecar in GitHub Actions).

Documented, non-violating references (left as-is):
- `skills/domino-apps/REACT-CICD.md` — `DOMINO_USER_API_KEY` / `X-Domino-Api-Key` for external GitHub Actions CI/CD (exempt).
- `skills/tags-and-properties/SKILL.md:45` — "Never use `DOMINO_USER_API_KEY`."
- `skills/domino-data-sdk/SKILL.md:170` and `DATASETS.md:24` — deprecation notes in env-var docs.
- `skills/domino-python-sdk/SKILL.md:65` — deprecation note.

### Rule 2 — Use Domino-injected environment variables for hosts

`your-domino.com` placeholders **resolved (2026-08-27):**

- [x] `skills/domino-ai-gateway/SKILL.md:83,104` — replaced with `f"{os.environ['DOMINO_API_HOST']}/api/aigateway/v1/openai"`.
- [x] `workflows/domino-app-init.md` (was `skills/domino-app-init/SKILL.md:61`) — replaced with `$DOMINO_API_HOST`.
- [x] `skills/domino-apps/SKILL.md:128` — replaced with `f"{API_HOST}/..."` (API_HOST set from env).
- [x] `skills/domino-data-sdk/SKILL.md:180` — removed (replaced with token-file auth).
- [x] `skills/domino-model-endpoints/SKILL.md:97` — replaced with `$DOMINO_API_HOST`.
- [x] `skills/domino-python-sdk/SKILL.md:72,79` — removed (deprecated auth block deleted).

Additional supporting files:
- [x] `skills/domino-apps/REACT-CICD.md:172` — replaced with real Domino URL scheme.
- [x] `skills/domino-apps/REACT-VITE-GUIDE.md:106` — replaced with `$DOMINO_API_HOST`.
- [x] `skills/domino-data-connectivity/AZURE-CREDENTIALS.md:57` — replaced with `$DOMINO_API_HOST`.
- [x] `skills/domino-model-endpoints/DEPLOY-ENDPOINT.md:250,308,388` — replaced with `$DOMINO_API_HOST`.
- [x] `skills/domino-model-endpoints/SCALING.md:307` — replaced with `$DOMINO_API_HOST`.
- [x] `skills/domino-modeling-assistant/SETUP.md:35` — replaced with `$DOMINO_API_HOST`. **Correction (2026-08-31):** this specific substitution was itself wrong — the surrounding step is explicitly "Laptop Only" and `$DOMINO_API_HOST` is unset there (Rule 7). Fixed properly on 2026-08-31 by switching that whole section to `~/.domino/.env`.
- [x] `skills/domino-python-sdk/API-APPS.md:63` — replaced with `$DOMINO_API_HOST`.
- [x] `skills/domino-python-sdk/API-MODELS.md:95,299` — replaced with `$DOMINO_API_HOST`.
- [x] `skills/domino-python-sdk/API-REFERENCE.md:26` — replaced with `$DOMINO_API_HOST`.

**Found and fixed 2026-08-31:**
- [x] `skills/domino-model-endpoints/DEPLOY-ENDPOINT.md:410,413` — `https://domino.com/...` placeholder (a variant the 2026-08-27 `your-domino.com` grep didn't catch) — replaced with `$DOMINO_API_HOST`.

Zero `your-domino.com` / `domino.com` placeholders remain in any skill or workflow file.

### Rule 3 — Don't use the `python-domino` SDK in examples

`from domino import Domino` outside the SDK-reference skills **resolved (2026-08-27):**

- [x] `skills/domino-apps/REACT-CICD.md:192` — converted to `requests` with REST API (projects endpoint).
- [x] `skills/domino-datasets/SKILL.md:41` — replaced with REST (`/api/datasetrw/v2/datasets`).
- [x] `skills/domino-distributed-computing/SKILL.md:61` — replaced with REST (`/api/jobs/v1/jobs`).
- [x] `skills/domino-model-monitoring/SKILL.md:216` — replaced with REST (`/api/jobs/v1/jobs`).
- [x] `skills/domino-model-endpoints/DEPLOY-ENDPOINT.md:247` — replaced with REST (`/api/modelServing/v1/modelApis`).
- [x] `skills/domino-projects/SKILL.md:46` — replaced with REST (`/api/projects/beta/projects`).
- [x] `skills/domino-workspaces/SKILL.md:45` — replaced with REST (`/api/jobs/v1/jobs`).
- [x] `skills/domino-workspaces/JUPYTER.md:27` — replaced with REST (`/api/jobs/v1/jobs`).
- [x] `skills/domino-workspaces/VSCODE.md:26` — replaced with REST (`/api/jobs/v1/jobs`).

**Found and fixed 2026-08-31:** `skills/domino-jobs/SKILL.md` was listed as
"clean" in the 2026-08-27 pass because the static check only greps for the
literal string `from domino import Domino` — this file called
`domino.runs_get_logs(run_id)`, `domino.runs_status(run_id)`, and
`domino.runs_stop(run_id)` (lines ~192, 272, 279) without ever importing
`domino`, which is both a Rule 3 violation in spirit and simply non-runnable
example code. Converted all three to REST calls reusing the file's existing
`TOKEN`/`BASE`/`headers` pattern. The `runs/.../stop` endpoint used there is
unverified — flagged inline per Rules 4/5.

Rule 3 is **N/A** for `domino-python-sdk` and `domino-data-sdk` — those skills
exist specifically to document the SDKs (and should mark supported vs
deprecated methods). `domino-data-sdk/VECTORDB.md` uses `domino_data`, the
data SDK, not `python-domino`.

### Rule 7 — Don't assume workspace-only env vars are set

**Correction (2026-08-31):** the 2026-08-27 entry below claiming this rule
was "resolved, 0 skills affected" was false. That pass only fixed six
skills' *swagger-fetch* examples specifically; it never swept the rest of
the repo for other unconditional `$DOMINO_API_HOST` usage. An adversarial
review on 2026-08-31 found the gap in eleven more files:

- [x] `skills/domino-python-sdk/API-ADMIN.md`, `API-APPS.md`, `API-DATASETS.md`, `API-ENVIRONMENTS.md`, `API-JOBS.md`, `API-MODELS.md`, `API-PROJECTS.md` — shared `## Authentication` block, all fixed with the same inline comment.
- [x] `skills/domino-apps/TROUBLESHOOTING.md` — app-logs curl example.
- [x] `skills/tags-and-properties/SKILL.md`, `PROPERTIES.md`, `PROPERTY-VALUES.md` — taxonomy swagger-fetch examples.
- [x] `skills/netapp-volumes/SKILL.md` — JWT-derived `CLUSTER_URL` flow needs `localhost:8899`, which also doesn't exist on the laptop; added a laptop-side branch (API-key auth against the `list_domino_clusters`-resolved host) rather than just a comment, since the whole approach (not just the host) differs.
- [x] `skills/domino-datasets/SKILL.md`, `domino-distributed-computing/SKILL.md`, `domino-launchers/SKILL.md` — REST job/dataset/launcher examples.
- [x] `skills/domino-model-endpoints/SKILL.md`, `DEPLOY-ENDPOINT.md` (already had it in most spots), `SCALING.md` — endpoint-calling and load-test examples.

Originally resolved (2026-08-27), still correct:
- [x] `skills/domino-apps/SKILL.md`, `domino-jobs/SKILL.md`, `domino-python-sdk/SKILL.md`, `domino-python-sdk/API-REFERENCE.md`, `domino-ai-gateway/SKILL.md`, `domino-ui-design/SKILL.md` — swagger-fetch examples, laptop path shown.

`domino-governance` didn't need this — it already derives its API base from
the JWT `iss` claim, which works in either context.

## Per-rule totals

| Rule | Skills affected (static) |
|------|--------------------------|
| 1 — Auth (drop `X-Domino-Api-Key` / `DOMINO_USER_API_KEY`) | 0 _(resolved)_ |
| 2 — Host env vars (drop placeholder hosts) | 0 _(resolved, including the `domino.com` variant found 2026-08-31)_ |
| 3 — Drop `python-domino` SDK examples | 0 _(resolved, including `domino-jobs` found 2026-08-31)_ |
| 4 — Verified API endpoints | not statically auditable — verify per-PR |
| 5 — Smoke-tested payloads | not statically auditable — verify per-PR |
| 7 — Workspace-only env vars need a laptop-side alternative | 0 _(resolved 2026-08-31, after the 2026-08-27 pass missed 11 files)_ |

## How to retrofit

When fixing a skill:

1. Read [CONTRIBUTING.md § Skill Authoring Standards](./CONTRIBUTING.md#skill-authoring-standards)
2. For Rule 1: replace `X-Domino-Api-Key` / `DOMINO_USER_API_KEY` examples with
   the `localhost:8899/access-token` → `Authorization: Bearer $TOKEN` pattern
   (or delete the deprecated example in the SDK-reference skills).
3. For Rule 2: substitute `$DOMINO_API_HOST` (or
   `$DOMINO_REMOTE_FILE_SYSTEM_HOSTPORT` for remotefs) for any host placeholder.
   Grep for both `your-domino` and bare `domino.com` — either can slip through.
4. For Rule 3: replace SDK calls with `curl` or `requests` examples. Don't
   trust a clean grep for `from domino import Domino` alone — also check for
   bare `domino.<method>()` calls with no import, which are just as broken
   and won't match that pattern.
5. For Rule 4 / 5: verify each endpoint path and payload against the current
   API docs and run a smoke-test.
6. For Rule 7: if an example uses `$DOMINO_API_HOST` (or assumes
   `localhost:8899` is reachable) and is meant to be run directly rather than
   only shown as in-workspace sample code, it needs a laptop-side alternative
   via `list_domino_clusters` — regardless of whether it's a swagger-fetch
   example specifically. Checking only for the literal swagger-fetch shape is
   how the 2026-08-27 pass missed 11 files.
7. Re-run the relevant skill end-to-end and confirm it activates correctly.
8. Tick the box(es) above and remove the skill from the list when zero
   violations remain.
