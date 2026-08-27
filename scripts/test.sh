#!/usr/bin/env bash
# Run the domino-cline-plugin test suite from any directory on this Mac.
#
# pytest only honors the `testpaths` ini option when invoked from the repo
# root (the directory containing pytest.ini). This wrapper resolves the repo
# root from this script's own location (not your $PWD), so it works whether
# you call it by absolute path, a relative path, or through a symlink.
set -euo pipefail

# Resolve this script's real location (handles relative paths and symlinks).
SOURCE="${BASH_SOURCE[0]}"
while [ -L "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

exec "$REPO_ROOT/mcp-servers/domino_mcp_server/.venv/bin/python" -m pytest "$@"
