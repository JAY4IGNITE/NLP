# ====================================================================
# CampusAI Local PowerShell Runner
# ====================================================================
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "         CampusAI: Autonomous Academic Intelligence System          " -ForegroundColor Yellow
Write-Host "                Aditya University (Surampalem)                      " -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Starting local server on http://localhost:8000 ..." -ForegroundColor Green
Write-Host ""
Write-Host "  * Interactive Student Web App:  http://localhost:8000/" -ForegroundColor White
Write-Host "  * Interactive Swagger API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "  * System Health Check:           http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "  (Press Ctrl+C to stop the server)" -ForegroundColor Gray
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
