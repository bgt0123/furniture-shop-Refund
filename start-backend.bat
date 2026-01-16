@echo off
cd backend
python -m uvicorn src.main:app --host 127.0.0.1 --port 3000