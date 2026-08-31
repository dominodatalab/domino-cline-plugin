# Domino App Init

Initialize a Domino-ready web application with the correct configuration for
Domino's reverse proxy. Invoke with `/domino-app-init` (optionally followed by
a framework name, e.g. `/domino-app-init react`).

## Supported Frameworks

- `react` or `vite-react` - React application with Vite (default)
- `streamlit` - Streamlit application
- `dash` - Plotly Dash application
- `flask` - Flask application
- `gradio` - Gradio application

## Steps

1. **Detect or ask for framework choice** — if not given as an argument, ask.
2. **Create app.sh** - Entry point script for Domino.
3. **Configure port binding** - Uses port 8888 by default (flexible).
4. **Set up proxy-compatible settings** - For React: `base: './'`.
5. **Create .env.example** - Template for environment variables.
6. **Add Model API integration** - Code for calling model endpoints, if the
   user wants it.

If run with no framework specified, ask for:
1. **Framework selection** - Which framework to use.
2. **Project name** - Name for the project/app.
3. **Include Model API** - Whether to include model API integration code.
4. **Model API URL** - If including, the endpoint URL to use.

## React/Vite Output

### vite.config.js
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './',
  server: { host: '0.0.0.0', port: 8888, strictPort: true },
  preview: { host: '0.0.0.0', port: 8888, strictPort: true },
  build: { outDir: 'dist', assetsDir: 'assets' }
})
```

### app.sh
```bash
#!/bin/bash
set -e
cd /mnt/code
npm ci
npm run build
npx serve -s dist -l 8888 --no-clipboard
```

### .env.example
```
VITE_MODEL_API_URL=https://$DOMINO_API_HOST/models/MODEL_ID/latest/model
VITE_MODEL_API_TOKEN=your_api_token
```

## Streamlit Output

### app.sh
```bash
#!/bin/bash
set -e
streamlit run app.py \
    --server.port 8888 \
    --server.address 0.0.0.0 \
    --server.headless true
```

## Dash Output

### app.py (with Domino configuration)
```python
import os
from dash import Dash, html

app = Dash(__name__)
app.layout = html.Div([html.H1("Domino Dash App")])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8888, debug=False)
```

### app.sh
```bash
#!/bin/bash
set -e
python app.py
```

## Flask Output

### app.py (with Domino configuration)
```python
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Domino Flask App"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=False)
```

### app.sh
```bash
#!/bin/bash
set -e
python app.py
```

## Post-Initialization Steps

After running this workflow, tell the user to:

1. **Configure environment variables** in Domino project settings.
2. **Set app.sh as the app entry point** when publishing the app.
3. **Test locally** using `./app.sh` before deploying.
4. **Verify port 8888** is being used correctly.

## Related

- `/domino-debug-proxy` - Diagnose proxy/routing issues in an app this
  workflow created (or any existing app).
- `/domino-experiment-setup`, `/domino-trace-setup` - Set up ML/GenAI
  tracking instead of (or alongside) a web app.
- `domino-apps` skill - Deeper framework/CI-CD/troubleshooting reference.
