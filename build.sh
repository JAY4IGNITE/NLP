#!/usr/bin/env bash
# ==============================================================================
# Native Render Build Script for CampusAI
# ==============================================================================
set -o errexit

echo "===> [1/4] Upgrading pip and installing lightweight CPU PyTorch..."
python -m pip install --upgrade pip
python -m pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

echo "===> [2/4] Installing application Python dependencies..."
python -m pip install --no-cache-dir -r requirements.txt

echo "===> [3/4] Building React Frontend..."
cd frontend
npm install --legacy-peer-deps
npm run build
cd ..

echo "===> [4/4] Verifying database schema and models..."
python -c "from backend.database.connection import create_all_tables; create_all_tables(); print('Database tables ready.')"

echo "===> Build completed successfully! Ready for launch."

