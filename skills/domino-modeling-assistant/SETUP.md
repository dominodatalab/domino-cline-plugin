# Complete Modeling Assistant Setup Guide

This guide covers setup for the Domino modeling assistant. The Domino MCP
Server lives in this plugin's `mcp-servers/domino_mcp_server/`, but it is
**not** auto-registered — register it once via Cline's MCP Servers settings
(see this repo's top-level README § Install), then it starts automatically
for every Cline session from then on.

**Inside a Domino workspace:** Everything is auto-detected (project, auth, DFS/Git mode). Skip straight to [Step 3: Test the Integration](#step-3-test-the-integration).

**Outside Domino (laptop):** You need Domino credentials configured and a project settings file. Follow the full guide below.

## Prerequisites

- Domino Data Lab account with API access
- [Cline](https://cline.bot) (VS Code extension) with this plugin's skills and MCP server installed (see README § Install)
- Python 3.11+
- `uv` package manager ([install guide](https://github.com/astral-sh/uv))
- Git

## Step 1: Set Domino Credentials (Laptop Only)

> **Skip this step if you are working inside a Domino workspace.** Authentication is handled automatically via ephemeral tokens.

### Generate API Key

1. Log into Domino
2. Go to **Account Settings** (click your profile icon)
3. Navigate to **API Keys**
4. Click **Generate New Key**
5. Copy and save the key securely

### Configure `~/.domino/.env`

This plugin's MCP server reads credentials from `~/.domino/.env` (not shell
environment variables). For a single Domino instance:

```bash
DOMINO_HOST="https://<your-instance>.cs.domino.tech"
DOMINO_API_KEY="your_api_key_here"
```

If you work against more than one Domino instance, use the multi-cluster form
instead (`DOMINO_CLUSTERS=alias1,alias2` plus per-alias `DOMINO_HOST_<ALIAS>`/
`DOMINO_API_KEY_<ALIAS>`) — see the README § Install and the `domino-teleport`
skill's cluster registry. Every `domino_server` MCP tool then takes an
optional `cluster` argument; call `list_domino_clusters` to see what's
configured.

No shell profile edits and no separate `.env` file inside this plugin's
directory are needed once `~/.domino/.env` is filled in — the MCP server
picks it up on the next call.

## Step 2: Configure Your Project (Laptop Only)

> **Skip this step if you are working inside a Domino workspace.** The project owner, project name, and DFS/Git mode are auto-detected from platform environment variables.

### Create Project Settings

In your Domino project directory, create `domino_project_settings.md`:

```markdown
# Domino Project Settings

## Project Information
- **Project Owner**: your-username
- **Project Name**: your-project-name

## Default Configuration
- **Compute Environment**: Default Python 3.10
- **Hardware Tier**: small-k8s

## Data Locations
- Input data: /mnt/data/
- Imported datasets: /mnt/imported/data/
- Output artifacts: /mnt/artifacts/

## Notes
- Always commit changes before running Domino jobs
- Use MLflow for experiment tracking
```

## Step 3: Test the Integration

### Create a Test Script

In your project, create `test_domino.py`:

```python
import os
print("Hello from Domino!")
print(f"Project: {os.environ.get('DOMINO_PROJECT_NAME', 'unknown')}")
print(f"User: {os.environ.get('DOMINO_STARTING_USERNAME', 'unknown')}")
```

### Commit the Script

```bash
git add test_domino.py
git commit -m "Add test script for modeling assistant"
git push
```

### Run via Your AI Assistant

Prompt:
```
Run test_domino.py as a Domino job
```

The MCP server should:
1. Create a Domino job
2. Execute the script
3. Return the output

## Step 4: Set Up Domino Environment (Optional)

### Option A: Domino Standard Environment with AI Tools (Recommended)

If your Domino instance has the **Standard Environment with AI Tools** available, use that — it comes preconfigured with everything needed for the modeling assistant workflow. No additional setup required.

In your Domino project:

1. Go to **Settings** → **Compute Environment**
2. Select the **Standard Environment with AI Tools** from the list

### Option B: Custom Vibe Modeling Image (Fallback)

If you don't have access to the Standard Environment with AI Tools, use the custom Docker image instead.

In your Domino project:

1. Go to **Settings** → **Compute Environment**
2. Create new environment with base image:
   ```
   quay.io/domino/field:vibe-modeling
   ```

This image includes:
- MCP server dependencies
- Common ML libraries
- Preconfigured for modeling assistant workflows

## Workflow Example

### Complete Modeling Assistant Session

1. **Start in your AI assistant** with your project open

2. **Analyze data** (prompt):
   ```
   Load the sales data from /mnt/data/sales.csv and show me
   a summary of the key metrics
   ```

3. **Assistant creates script**, commits, runs in Domino

4. **Review results** returned through MCP

5. **Iterate on analysis** (prompt):
   ```
   Now create a visualization of sales by region and save it
   to /mnt/artifacts/sales_by_region.png
   ```

6. **Train a model** (prompt):
   ```
   Train a random forest model to predict sales using the
   processed data. Log the results to MLflow.
   ```

7. **All work is tracked** in Domino's experiment manager

## Troubleshooting

### "MCP server not found" or tools not appearing

1. Ensure `uv` is installed and in your PATH
2. Open Cline's MCP Servers panel and confirm `domino_server` shows as
   registered and connected — if it's red/disconnected, click it to see the
   stdout/stderr log from the server process
3. Confirm the `--directory` argument in the MCP server registration is the
   absolute path to this plugin's `mcp-servers/domino_mcp_server/` on disk
   (see README § Install) — a stale or wrong path is the most common cause
4. Re-registering the server (remove and re-add in the MCP Servers panel)
   picks up code/config changes without needing to restart the VS Code window

### "Unauthorized" errors

1. **Workspace:** This shouldn't happen — auth is automatic. Restart the workspace if it persists.
2. **Laptop:** Verify `~/.domino/.env` has `DOMINO_API_KEY`/`DOMINO_HOST` (or the `DOMINO_CLUSTERS` multi-cluster form) set correctly — call the `check_domino_api_access` MCP tool to confirm

### "Project not found"

1. **Workspace:** Project info is auto-detected. Check that `DOMINO_PROJECT_OWNER` and `DOMINO_PROJECT_NAME` env vars are set.
2. **Laptop:** Check that `domino_project_settings.md` exists in your project root with the correct owner and project name.

### Jobs fail immediately

1. Check compute environment is available
2. Verify hardware tier is valid
3. Review Domino job logs for errors

## Next Steps

- [SKILL.md](./SKILL.md) - Overview of modeling assistant capabilities and MCP server tool reference
- [Domino Blueprints](https://domino.ai/resources/blueprints/vibe-modeling) - Official documentation
