#!/usr/bin/env bash
# Run main.py with environment variables loaded from the project's .env file.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "deploy_db.sh: missing env file at $ENV_FILE" >&2
    exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

if [[ -x "$PROJECT_ROOT/.venv/Scripts/python.exe" ]]; then
    PYTHON="$PROJECT_ROOT/.venv/Scripts/python.exe"
elif [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
    PYTHON="$PROJECT_ROOT/.venv/bin/python"
else
    PYTHON="${PYTHON:-python}"
fi

cd "$PROJECT_ROOT"
exec "$PYTHON" main.py "$@"
