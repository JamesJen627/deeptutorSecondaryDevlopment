# DeepTutor 开发环境初始化（Windows，只需运行一次）
# 用法: .\scripts\dev-install.ps1

$Python = "D:\python3.12\python.exe"
$Repo = "D:\Dev\deeptutorSecondaryDevlopment"

Write-Host "==> 停止可能占用 deeptutor.exe 的旧进程..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 8001,3782 -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2

Write-Host "==> pip install -e (后端)" -ForegroundColor Cyan
Set-Location $Repo
& $Python -m pip install -e .

Write-Host "==> npm install (前端)" -ForegroundColor Cyan
Set-Location "$Repo\web"
npm install

Write-Host "`n完成。启动请运行: .\scripts\dev-start.ps1" -ForegroundColor Green
