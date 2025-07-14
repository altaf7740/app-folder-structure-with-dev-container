#!/bin/bash 
cd /home/developer/workspace/frontend
npm install
npm run dev -- --host &
cd /home/developer/workspace
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload