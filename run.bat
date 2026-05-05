@echo off
echo Installing dependencies...
pip install -r requirements.txt

if not exist .env (
  echo Error: .env file not found in project root.
  exit /b 1
)

echo Running bot...
set PYTHONPATH=src

python -c "from app.main import run; run('BTC/USDT', use_mock=False)"
