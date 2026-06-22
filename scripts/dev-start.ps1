# DeepTutor 开发环境启动（Windows）
# 用法（PowerShell）: .\scripts\dev-start.ps1
# 用法（CMD）:        scripts\dev-start.bat

$Python = "D:\python3.12\python.exe"
$Deeptutor = "D:\python3.12\Scripts\deeptutor.exe"
$Workspace = "D:\Dev\DeepTutor"
$Repo = "D:\Dev\deeptutorSecondaryDevlopment"

if (-not (Test-Path $Deeptutor)) {
    Write-Error "找不到 deeptutor: $Deeptutor`n请先运行: $Python -m pip install -e $Repo"
    exit 1
}

if (-not (Test-Path $Workspace)) {
    Write-Warning "工作区目录不存在，将创建: $Workspace"
    New-Item -ItemType Directory -Path $Workspace -Force | Out-Null
}

Set-Location $Workspace
& $Deeptutor start --home $Workspace
