#!/bin/bash

set -e

echo "Installing dependencies..."
pip install -r requirements.txt

if [ ! -f .env ]; then
  echo "Error: .env file not found in project root."
  exit 1
fi

echo "Running bot..."

PYTHONPATH=src python - <<'PY'
from app.main import run

run("BTC/USDT", use_mock=False)
PY
