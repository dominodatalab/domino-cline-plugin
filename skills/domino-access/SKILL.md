---
name: domino-access
description: Check whether the current environment can reach a Domino cluster, following the standard three-leg protocol: REST API (first), then Teleport/kubectl, then AWS infrastructure. Use when asked "do you have access to this cluster", to verify connectivity/reachability to a Domino deployment, or when an API/Teleport/AWS call fails with an authentication or expiry error.
---

# Domino Access Check

Standard protocol for answering "do you have access to this cluster?" Run all
three legs **in this order of precedence** and report each one's status. Don't
stop silently after a single success — the point is a complete picture of
which paths work and which don't.

| Leg | What it proves | Primary command(s) |
|---|---|---|
| 1. REST API | You can reach the platform's API and your key is valid | MCP tools below |
| 2. Teleport | You can reach the cluster's Kubernetes control plane | `tsh status`, `tsh kube ls` |
| 3. AWS | You can inspect the underlying infra (EKS/S3/EFS/CloudWatch) | `aws sts get-caller-identity` |

## Leg 1 — REST API

```text
1. Call the `list_domino_clusters` MCP tool (domino_server) to see what's configured.
2. Map the user's named host/alias to a cluster alias. If the host isn't in the
   list, say so and stop — don't guess a cluster.
3. Call `check_domino_api_access(cluster=<alias>)`.
   - access: true  -> ✅ API reachable and key valid.
   - access: false, status 401/403 -> 🔑 prompt:
       "Your API key for <alias> is expired or invalid. Regenerate it at
        <host>/account/settings/api-keys and update ~/.domino/.env
        (DOMINO_API_KEY_<ALIAS>=...)."
   - access: false, connection error/timeout -> ⚠️ cluster unreachable from here.
       Confirm the host is correct and that the cluster is up.
```

Never fall back to `curl` with the raw API key — the MCP tool does the auth
server-side so the key never enters the conversation.

## Leg 2 — Teleport / kubectl

```text
1. `tsh status`        — confirm a session exists and which proxy it's on.
2. `tsh kube ls`       — confirm the target kube cluster is listed.
3. `kubectl cluster-info` — quick end-to-end check that the context resolves.

Not logged in -> prompt:
    tsh login --proxy=dominodatalab.teleport.sh:443   (6.3+ clusters)
    tsh7 login --proxy=dev-teleport.domino.tech:443   (6.2 clusters)
    then: tsh kube login <teleport-cluster-name>      (both steps required)

Cluster not listed -> wrong proxy, wrong teleport_cluster_name, or your role
has no kube access for it. See the `domino-teleport` skill for the registry
and the version -> proxy/binary mapping.
```

## Leg 3 — AWS infrastructure

```text
1. `aws sts get-caller-identity`
   - Shows account 946429944765 and role okta-fulladmin -> ✅ active session.
   - ExpiredToken / "security token ... is expired" -> prompt:
       run `okta-aws` (interactive browser OIDC) to re-auth.
```

## Re-auth on expiry (cross-cutting)

Authentication for all three legs expires periodically. If **any** leg fails
with an authentication/expiry error, the first response is to prompt the user
to re-auth **that specific path** — don't assume the failure is something else
and start debugging blind:

- API 401/403      -> regenerate key, update `~/.domino/.env`
- Teleport expired -> `tsh login` / `tsh7 login` (+ `tsh kube login`)
- AWS expired      -> `okta-aws`

Only after the credential/session is confirmed valid should you investigate
network, config, or infrastructure causes.
