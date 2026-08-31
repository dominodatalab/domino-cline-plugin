# Domino Debug Proxy

Diagnose and fix common Domino proxy and routing issues for web applications.
Invoke with `/domino-debug-proxy` in a project containing a web app (checks
`vite.config.js`, `package.json`, and `app.sh`).

## Checks to run

### 1. Port Configuration
- Verifies port 8888 is used.
- Checks for hardcoded ports in config files.
- Validates strictPort settings.

### 2. Base Path Configuration
- For React/Vite: checks `base: './'` in vite.config.js.
- For other frameworks: checks relative path usage.

### 3. Host Binding
- Verifies `host: '0.0.0.0'` (not localhost or 127.0.0.1).
- Checks server configuration in all frameworks.

### 4. app.sh Analysis
- Checks for correct working directory.
- Verifies build commands.
- Validates serve configuration.

### 5. Asset Loading
- Checks for hardcoded absolute paths.
- Verifies relative asset references.

## Common issues and fixes

### Issue: Wrong Port

**Symptom:** App shows "Connection refused"

**Detection:** port 3000 (or similar) found in vite.config.js; expected 8888.

**Fix:**
```javascript
server: {
  port: 8888,
  strictPort: true
}
```

### Issue: Absolute Base Path

**Symptom:** 404 errors on CSS/JS files

**Detection:** vite.config.js has `base: '/'` or no `base` specified — causes
asset 404s behind Domino's proxy.

**Fix:**
```javascript
export default defineConfig({
  base: './',
  // ...
})
```

### Issue: Localhost Binding

**Symptom:** App not accessible from browser

**Detection:** Server bound to localhost/127.0.0.1 — Domino's proxy cannot
reach the app.

**Fix:**
```javascript
server: {
  host: '0.0.0.0',
  // ...
}
```

### Issue: Missing SPA Fallback

**Symptom:** Direct URL access returns 404

**Detection:** app.sh uses `npx serve dist` without the `-s` flag — client-side
routing will fail.

**Fix:**
```bash
npx serve -s dist -l 8888
```

### Issue: Build Not Running

**Symptom:** Blank page or old content

**Detection:** app.sh is missing the `npm run build` step — app may be serving
stale or no content.

**Fix:**
```bash
#!/bin/bash
set -e
cd /mnt/code
npm ci
npm run build  # Add this line
npx serve -s dist -l 8888
```

## Reporting

After running the checks, report a summary in this shape (adapt to what was
actually found):

```
Domino Proxy Debug Report
==========================

Checking: vite.config.js
✅ Port: 8888
✅ Base path: './'
✅ Host: 0.0.0.0

Checking: app.sh
✅ Working directory: /mnt/code
✅ Build command: npm run build
❌ Serve command missing -s flag

Checking: package.json
✅ serve dependency present
✅ Build script defined

Summary: found 1 issue.

Recommended fix — update app.sh serve command:
  - Current: npx serve dist -l 8888
  + Fixed:   npx serve -s dist -l 8888
```

Ask before applying fixes automatically; offer to apply each one individually
rather than all at once if there's more than one.

## Manual investigation

For issues that can't be auto-fixed, provide:

1. **Browser console commands** to run for debugging.
2. **Network tab guidance** for checking requests.
3. **Log locations** to check in Domino.

## Related

- `/domino-app-init` - Initialize a new app with correct settings from the start.
- `/domino-experiment-setup` - Set up experiment tracking.
- `/domino-trace-setup` - Set up GenAI tracing.
- `domino-apps` skill - Deeper framework/CI-CD reference used alongside this.
