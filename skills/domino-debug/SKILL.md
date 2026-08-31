---
name: domino-debug
description: Debug Domino issues including app deployment problems, job failures, environment build errors, and connectivity issues. Use when troubleshooting errors or unexpected behavior in Domino.
---

# Domino Debug

Diagnose and fix issues with Domino workloads: application deployment
failures, job execution errors, environment build issues, data connectivity
problems, model endpoint errors, workspace issues, and API failures. For
deployment-specific fixes see the `domino-apps` skill; for environment build
issues see `domino-environments`; for job configuration see `domino-jobs`.

## Diagnostic Approach

For each issue, follow this process:

### 1. Gather Information
- What is the exact error message?
- When did the issue start?
- What changed recently?
- What logs are available?

### 2. Check Common Causes

#### App Deployment Issues
- Port binding (must be 0.0.0.0)
- Base path configuration
- Missing dependencies
- app.sh syntax errors
- File permissions

#### Job Failures
- Script syntax errors
- Missing files or imports
- Hardware tier limits
- Environment compatibility
- Timeout issues

#### Environment Build Errors
- Dockerfile syntax
- Package conflicts
- Network access during build
- Base image compatibility
- Permission issues

#### Data Connectivity
- Credential configuration
- Network policies
- Path mounting
- Permission grants

### 3. Provide Solutions
- Identify root cause
- Suggest specific fixes
- Provide code/config changes
- Explain why the fix works

## Common Error Patterns

| Error Pattern | Likely Cause | Solution |
|--------------|--------------|----------|
| "Connection refused" | Wrong host/port binding | Bind to 0.0.0.0 |
| "Module not found" | Missing dependency | Add to environment |
| "Permission denied" | File permissions | chmod or ownership |
| "Build failed" | Dockerfile error | Check syntax/packages |
| "Timeout" | Long-running operation | Increase timeout/optimize |

## Workflow

1. Understand the reported issue
2. Request relevant logs or error messages
3. Analyze the error pattern
4. Check configuration files
5. Identify root cause
6. Provide step-by-step fix
7. Suggest preventive measures
