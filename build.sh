#!/usr/bin/env bash
# ==============================================================================
# Native Render Build Script for CampusAI
# ==============================================================================
set -o errexit

echo "===> [1/3] Upgrading pip..."
python -m pip install --upgrade pip

echo "===> [2/3] Installing Python dependencies (CPU PyTorch)..."
python -m pip install --no-cache-dir -r requirements.txt

# If npm is present, rebuild frontend; otherwise use prebuilt frontend/dist
if command -v npm &> /dev/null; then
  echo "===> Building React Frontend..."
  cd frontend
  npm install --legacy-peer-deps
  npm run build
  cd ..
else
  echo "===> Using pre-built production frontend assets in frontend/dist"
fi

echo "===> [3/3] Verifying database schema..."
python -c "from backend.database.connection import create_all_tables; create_all_tables(); print('Database tables verified.')"

echo "===> Build completed successfully! Ready for launch."
