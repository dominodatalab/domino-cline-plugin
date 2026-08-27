---
name: domino-docs
description: Look up Domino Data Lab's official product documentation (docs.dominodatalab.com) for conceptual/product questions — how a feature works, what a setting or config option does, admin/user guide topics. Use for "how does X work in Domino" questions not answered by a more specific domino-* skill, or to confirm platform behavior rather than assume it.
---

# Domino Product Docs

Customer-facing product documentation, fetched live via `web_fetch` — not a
substitute for the swagger (endpoint schemas — see the domino-* API skills
and the global Cline rule) and not for internal engineering/ops docs
(Fleetcommand, Teleport setup, ENG-space how-tos — that's Confluence via the
"Domino Atlassian" MCP server, already configured in Cline).

## Site structure

Base: `https://docs.dominodatalab.com/`

Four top-level guides, each versioned:
- **User Guide** — data-scientist-facing: workspaces, jobs, projects, apps,
  experiments, governance
- **Admin Guide** — configuration and platform management
- **API Guide** — developer-facing reference and workflow context (the
  swagger itself is the schema source of truth; this is the prose context
  around it)
- **Release Notes** — what changed between versions

Versions available: Cloud (current), 6.2, 6.1, 6.0, 5.11, 5.10. No
confirmed search endpoint on the site — if the exact page isn't known,
either navigate from a guide's table of contents or fall back to a general
web search scoped to the site (`site:docs.dominodatalab.com <topic>`)
rather than guess a URL.

## Which version to fetch

**Don't default to "latest"/Cloud automatically.** If the question is about
a specific cluster's behavior, match the docs version to that cluster's
`domino_version` from the `domino-teleport` skill's registry — a 6.2
cluster may not behave like current Cloud docs describe. Only default to
Cloud/current for genuinely version-agnostic conceptual questions with no
specific cluster in play.

## When this fires vs. when it doesn't

- Conceptual/behavioral question about the platform → this skill.
- "What's the endpoint/schema for X" → the live swagger instead (see the
  domino-* API skills and the global Cline rule for how to resolve the
  cluster host from the laptop).
- Internal tool/process question (Fleetcommand, Teleport, ENG runbooks) →
  Confluence via the Atlassian MCP, not this skill.
