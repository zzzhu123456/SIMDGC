@echo off
cd /d "%~dp0"
echo 启动本地服务 http://127.0.0.1:8765/ ...
start "IMDG demo" /min cmd /c python -m http.server 8765 --bind 127.0.0.1 --directory web
timeout /t 2 >nul
start "" http://127.0.0.1:8765/