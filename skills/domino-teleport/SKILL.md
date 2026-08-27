---
name: domino-teleport
description: Access a Domino cluster's Kubernetes control plane via Teleport (tsh/tsh7) and kubectl. Use when connecting to a Domino cluster's Kubernetes layer, running kubectl against Domino infrastructure, or diagnosing Teleport login/version errors.
---

# Domino Teleport Access

Domino's Kubernetes clusters (EKS) are reached via Teleport, not directly
via `kubectl` or the AWS CLI. There are two incompatible Teleport
environments, keyed by Domino version:

| Domino version | Teleport proxy | Client binary |
|---|---|---|
| 6.2 | `dev-teleport.domino.tech` | `tsh7` (old client — separately installed) |
| 6.3+ | `dominodatalab.teleport.sh` | `tsh` (current client) |

Fleetcommand-created dev deployments register with the dev instance.

## Login sequence

**Both steps are required** — running only `tsh login` (auth) without
`tsh kube login` (kubectl context) is the most common failure mode:

```bash
# 6.2 clusters
tsh7 login --proxy=dev-teleport.domino.tech:443
tsh7 kube login <cluster-name>

# 6.3+ clusters
tsh login --proxy=dominodatalab.teleport.sh:443
tsh kube login <cluster-name>
```

After both steps, `kubectl` targets that cluster normally.

## Cluster registry

Same aliases as `~/.domino/.env`'s `DOMINO_CLUSTERS` —
one name per Domino instance across both the REST API config and this
skill. Fill in `domino_version` and `teleport_cluster_name` (the name
Teleport registers the kube cluster under — may differ from the alias)
for each; add a row here whenever a new alias is added to `DOMINO_CLUSTERS`.

| alias | domino_version | teleport_cluster_name |
|---|---|---|
| marcdo126967 | _fill in_ | _fill in_ |
| mikesn136713 | _fill in_ | _fill in_ |

> **TODO:** fill in `domino_version` and `teleport_cluster_name` above so
> access checks can be automated. Until they're filled, the `domino-access`
> skill will ask for these values when a Teleport leg is requested.

For the overall "do you have access to this cluster" workflow (REST API →
Teleport → AWS, in that order), see the `domino-access` skill.

If asked to access a cluster not in this table, ask which Domino version
it runs (or its Teleport cluster name) rather than guessing which tsh
binary/proxy to use — logging into the wrong Teleport instance is a dead
end, not a harmless mistake.

## Common namespace shortcuts

Once `kubectl` is pointed at a cluster:

| Namespace | Purpose |
|---|---|
| `domino-platform` | Domino's own platform services |
| `domino-compute` | End-user workloads (jobs, workspaces, apps) |
| `domino-field` | Field/professional-services tooling |
| `domino-operator` | The Domino operator itself |

e.g. `kubectl get pods -n domino-compute` to see running user workloads.
