@echo off
title CampusAI - Local Runner
cls
echo ====================================================================
echo          CampusAI: Autonomous Academic Intelligence System
echo                 Aditya University (Surampalem)
echo ====================================================================
echo.
echo  Starting local server on http://localhost:8000 ...
echo.
echo  * Interactive Student Web App:  http://localhost:8000/
echo  * Interactive Swagger API Docs:  http://localhost:8000/docs
echo  * System Health Check:           http://localhost:8000/health
echo.
echo  (Press CTRL+C to stop the server)
echo ====================================================================
echo.
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
