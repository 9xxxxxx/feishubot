# 强制终止Metabase服务
$PORT = 17608  # 必须与启动脚本端口一致

# 通过端口查找进程
$process = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue |
           Where-Object { $_.State -eq 'Listen' } |
           ForEach-Object { Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue } |
           Where-Object { $_.Path -like "*java*" }

if ($process) {
    $process | Stop-Process -Force
    Write-Host "Metabase service terminated (PID: $($process.Id))"
} else {
    Write-Host "No running Metabase found on port $PORT"
}

# 清理残留PID文件
if (Test-Path "metabase.pid") {
    Remove-Item "metabase.pid" -Force
}