@echo off
REM DeepTutor 开发环境启动（CMD 入口 — 会调用 PowerShell 执行 dev-start.ps1）
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0dev-start.ps1"
if errorlevel 1 pause
