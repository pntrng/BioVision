@echo off
REM Script để khởi động server local cho BioVision
echo === BioVision Local Server ===
echo.

REM Thiết lập environment variables
set ENV=development
set ADMIN_TOKEN=test-token-123

echo [INFO] Environment variables set:
echo   - ENV: %ENV%
echo   - ADMIN_TOKEN: test-****
echo.

echo [INFO] Starting Flask server...
echo.
echo Server will be available at:
echo   - Guest page: http://localhost:5000/
echo   - Admin page: http://localhost:5000/admin
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
