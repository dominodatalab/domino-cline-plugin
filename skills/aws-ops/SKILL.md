---
name: aws-ops
description: AWS CLI operations for inspecting Domino's underlying infrastructure — S3, EFS, EKS (where Domino's Kubernetes clusters run), CloudWatch logs, and other AWS services as encountered. Use when checking AWS resource/bucket/log status related to Domino infrastructure, or debugging via the AWS CLI.
---

# AWS Ops

A living reference for AWS CLI usage against Domino's infrastructure. Grows
over time — see "Extending this skill" below.

## Authentication

Session-based via Okta, not a static profile:

```bash
okta-aws   # alias for the okta-aws-cli flow
```

Authenticates into your organization's AWS admin role via interactive
browser-based OIDC (can't be triggered headlessly) — this is your own
existing Okta AWS CLI setup, not something this plugin installs or
configures. Sessions have a finite TTL; if a command suddenly starts
failing with an auth/expiry error, re-run `okta-aws` before assuming
anything else is wrong.

Set `AWS_OKTA_ACCOUNT_ID` and `AWS_OKTA_ROLE` in `~/.domino/.env` (see
`domino.env.example` and the README's "Configure credentials" section) so
the check below can confirm the session landed in the right place, not
just "a" place.

### Quick access check

```bash
aws sts get-caller-identity
```

- `Account` and role match `AWS_OKTA_ACCOUNT_ID` / `AWS_OKTA_ROLE` (if set) → ✅ active session, right account/role.
- Any other account/role → ⚠️ probably the wrong Okta profile — check which one `okta-aws` selected.
- `ExpiredToken` / `The security token included in the request is expired` → re-run `okta-aws`.

For the overall "do you have access to this cluster" workflow (REST API →
Teleport → AWS, in that order), see the `domino-access` skill.

## EKS

This is where Domino's Kubernetes clusters actually run — **but `kubectl`
access goes through Teleport, not directly through the AWS CLI or
`aws eks update-kubeconfig`.** See the `domino-teleport` skill for that.
Use the AWS CLI here for EKS control-plane/infra-level inspection instead:

```bash
aws eks describe-cluster --name <cluster-name>
aws eks list-nodegroups --cluster-name <cluster-name>
```

## S3

```bash
aws s3 ls s3://<bucket>/                       # list objects
aws s3api head-bucket --bucket <bucket>        # check a bucket exists/is reachable
aws s3api get-bucket-lifecycle-configuration --bucket <bucket>
```

## EFS

```bash
aws efs describe-file-systems
aws efs describe-mount-targets --file-system-id <fs-id>
```

## CloudWatch Logs

```bash
aws logs tail <log-group> --follow
aws logs filter-log-events --log-group-name <log-group> --filter-pattern "<pattern>"
```

## Extending this skill

If a task needs an AWS service or command pattern not yet documented
above:

1. Complete the task using general AWS CLI knowledge — the same
   `okta-aws` auth applies to every service.
2. Afterward, append a new `## <ServiceName>` section to **this file**
   (the `aws-ops` skill's `SKILL.md`, wherever this repo is cloned) documenting the
   commands used, what they're for, and anything Domino-specific learned
   along the way (bucket naming conventions, tags, cluster-specific
   quirks, etc.) — follow the format of the existing sections.
3. Say in your response that you added a new section, so it gets reviewed
   rather than silently accumulating.

This is a real file edit, not a suggestion to remember for later — the
point is that this skill should have more sections next month than it
does today.
