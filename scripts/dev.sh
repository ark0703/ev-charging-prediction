#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -f "models/model.joblib" ]; then
  echo "Model not found. Running training pipeline..."
  bash scripts/train.sh
fi

# shellcheck disable=SC1091
source .venv/bin/activate

cleanup() {
  kill "$API_PID" "$WEB_PID" 2>/dev/null || true
}
trap cleanup EXIT

uvicorn api.main:app --host 127.0.0.1 --port 8765 &
API_PID=$!

npm run dev:web &
WEB_PID=$!

wait
