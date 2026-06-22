@echo off
REM DeepTutor 开发环境初始化（CMD 入口）
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0dev-install.ps1"
if errorlevel 1 pause
