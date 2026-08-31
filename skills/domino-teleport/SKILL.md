---
name: domino-teleport
description: Access a Domino cluster's Kubernetes control plane via Teleport and kubectl, using scripts/domino-tsh to auto-select the right tsh binary version. Use when connecting to a Domino cluster's Kubernetes layer, running kubectl against Domino infrastructure, or diagnosing Teleport login/version errors.
---

# Domino Teleport Access

Domino's Kubernetes clusters (EKS) are reached via Teleport, not directly
via `kubectl` or the AWS CLI. Domino's Teleport instances span multiple
Teleport major versions (an old dev instance, current production, possibly
others over time), and Teleport strictly requires the `tsh` client be the
same major version as the server, or at most one behind — so more than one
`tsh` binary needs to be installed.

**Don't hand-pick which `tsh` binary to run, and don't assume any particular
binary name.** Use `scripts/domino-tsh` instead — it has no naming
convention baked in: it finds whatever tsh-like binaries are actually
installed, asks each its own version, asks the target proxy (via Teleport's
own unauthenticated discovery endpoint) what version *it* requires, and
picks whichever installed binary is compatible. This is deliberately
unopinionated so the plugin works regardless of what anyone happens to have
named their older client — it doesn't have to be `tsh7`.

## Usage

```bash
# Login + kube context, version-matched automatically:
/absolute/path/to/domino-cline-plugin/scripts/domino-tsh login <alias>

# See which binary/version it would use, without logging in:
/absolute/path/to/domino-cline-plugin/scripts/domino-tsh resolve <alias>
```

`login` runs both required steps (`tsh login` then `tsh kube login` —
skipping the second is the most common failure mode with plain `tsh`, this
script always does both). After that, `kubectl` targets the cluster
normally.

If it exits with "no installed tsh-like binary is compatible," that's not a
bug to route around — it means the right client version genuinely isn't
installed. It says which major version is needed; install that one.

## Cluster registry

Same aliases as `~/.domino/.env`'s `DOMINO_CLUSTERS` — one name per Domino
instance, shared across the REST API config and this script. Per alias:

- `TELEPORT_PROXY_<ALIAS>` — **required**. The Teleport proxy for that
  cluster (e.g. `dev-teleport.domino.tech:443`).
- `TELEPORT_CLUSTER_NAME_<ALIAS>` — optional, defaults to the alias. Set it
  if Teleport registers the kube cluster under a different name.

Nothing about the *tsh version* is tracked here anymore — `domino-tsh`
determines that live from the proxy each time, so it can't go stale if a
Teleport instance gets upgraded later.

If asked to access a cluster with no `TELEPORT_PROXY_<ALIAS>` set, ask which
proxy it's on rather than guessing — logging into the wrong Teleport
instance is a dead end, not a harmless mistake. `domino-tsh` will refuse
with a clear error rather than guess, too.

For the overall "do you have access to this cluster" workflow (REST API →
Teleport → AWS, in that order), see the `domino-access` skill.

## Common namespace shortcuts

Once `kubectl` is pointed at a cluster:

| Namespace | Purpose |
|---|---|
| `domino-platform` | Domino's own platform services |
| `domino-compute` | End-user workloads (jobs, workspaces, apps) |
| `domino-field` | Field/professional-services tooling |
| `domino-operator` | The Domino operator itself |

e.g. `kubectl get pods -n domino-compute` to see running user workloads.
