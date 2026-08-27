# Skill Audit — Compliance with Skill Authoring Standards

Regenerated for **domino-cline-plugin** (Cline) against the rules in
[CONTRIBUTING.md](./CONTRIBUTING.md#skill-authoring-standards).

This is a tracking checklist — it captures the work to be done, not fixes
landed here. Rules 4 (verified endpoints) and 5 (smoke-tested payloads) are
not statically auditable and must be verified per-PR; this file tracks the
static rules (1–3) plus the SDK-reference and CI/CD exceptions.

> **Note on provenance:** an earlier `SKILL_AUDIT.md` was copied verbatim from
> the Claude Code plugin (`domino-claude-plugin`) and referenced that repo's
> skill paths (`skills/jobs`, `skills/environments`, …). Those paths do not
> exist here — this repo prefixes skill directories with `domino-`. That copy
> was also dated 2026-05-08 and listed violations that have since been fixed
> (e.g. `jobs` and `launchers` auth violations). This file has been regenerated
> with correct paths and current line numbers.

## Clean skills (22)

No static violations (rules 1–3) in their `SKILL.md`:

- `skills/aws-ops/SKILL.md`
- `skills/domino-access/SKILL.md`
- `skills/domino-data-connectivity/SKILL.md`
- `skills/domino-debug/SKILL.md`
- `skills/domino-debug-proxy/SKILL.md`
- `skills/domino-deploy/SKILL.md`
- `skills/domino-environments/SKILL.md`
- `skills/domino-experiment-setup/SKILL.md`
- `skills/domino-experiment-tracking/SKILL.md`
- `skills/domino-flows/SKILL.md`
- `skills/domino-genai-tracing/SKILL.md`
- `skills/domino-governance/SKILL.md`
- `skills/domino-jobs/SKILL.md`
- `skills/domino-launchers/SKILL.md`
- `skills/domino-modeling-assistant/SKILL.md`
- `skills/domino-setup/SKILL.md`
- `skills/domino-teleport/SKILL.md`
- `skills/domino-trace-setup/SKILL.md`
- `skills/domino-ui-bootstrap/SKILL.md`
- `skills/domino-ui-design/SKILL.md`
- `skills/netapp-volumes/SKILL.md`
- `skills/tags-and-properties/SKILL.md`

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
- [x] `skills/domino-app-init/SKILL.md:61` — replaced with `$DOMINO_API_HOST`.
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
- [x] `skills/domino-modeling-assistant/SETUP.md:35` — replaced with `$DOMINO_API_HOST`.
- [x] `skills/domino-python-sdk/API-APPS.md:63` — replaced with `$DOMINO_API_HOST`.
- [x] `skills/domino-python-sdk/API-MODELS.md:95,299` — replaced with `$DOMINO_API_HOST`.
- [x] `skills/domino-python-sdk/API-REFERENCE.md:26` — replaced with `$DOMINO_API_HOST`.

Zero `your-domino` remain in any skill file.

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

Rule 3 is **N/A** for `domino-python-sdk` and `domino-data-sdk` — those skills
exist specifically to document the SDKs (and should mark supported vs
deprecated methods). `domino-data-sdk/VECTORDB.md` uses `domino_data`, the
data SDK, not `python-domino`.

## Per-rule totals

| Rule | Skills affected (static) |
|------|--------------------------|
| 1 — Auth (drop `X-Domino-Api-Key` / `DOMINO_USER_API_KEY`) | 0 _(all resolved)_ |
| 2 — Host env vars (drop `your-domino.com` placeholders) | 0 _(all resolved)_ |
| 3 — Drop `python-domino` SDK examples | 0 _(all resolved)_ |
| 4 — Verified API endpoints | not statically auditable — verify per-PR |
| 5 — Smoke-tested payloads | not statically auditable — verify per-PR |

## How to retrofit

When fixing a skill:

1. Read [CONTRIBUTING.md § Skill Authoring Standards](./CONTRIBUTING.md#skill-authoring-standards)
2. For Rule 1: replace `X-Domino-Api-Key` / `DOMINO_USER_API_KEY` examples with
   the `localhost:8899/access-token` → `Authorization: Bearer $TOKEN` pattern
   (or delete the deprecated example in the SDK-reference skills).
3. For Rule 2: substitute `$DOMINO_API_HOST` (or
   `$DOMINO_REMOTE_FILE_SYSTEM_HOSTPORT` for remotefs) for any host placeholder.
4. For Rule 3: replace SDK calls with `curl` or `requests` examples.
5. For Rule 4 / 5: verify each endpoint path and payload against the current
   API docs and run a smoke-test.
6. Re-run the relevant skill end-to-end and confirm it activates correctly.
7. Tick the box(es) above and remove the skill from the list when zero
   violations remain.