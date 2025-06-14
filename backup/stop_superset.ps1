# 查找所有名为 'waitress-serve' 的进程
$processes = Get-Process -Name "waitress-serve" -ErrorAction SilentlyContinue

# 输出找到的进程信息
if ($processes) {
    Write-Host "Found the following 'waitress-serve' processes:"
    foreach ($process in $processes) {
        Write-Host "PID: $($process.Id), Process Name: $($process.ProcessName)"
    }
} else {
    Write-Host "No 'waitress-serve' processes are running."
}

# 终止所有找到的进程
if ($processes) {
    foreach ($process in $processes) {
        try {
            Stop-Process -InputObject $process -Force -ErrorAction Stop
            Write-Host "Successfully terminated process with PID: $($process.Id)"
        } catch {
            Write-Host "Failed to terminate process with PID: $($process.Id). Error: $_"
        }
    }
}

# 等待2秒确保进程终止
Start-Sleep -Seconds 2

# 验证进程是否完全终止
$remainingProcesses = Get-Process -Name "waitress-serve" -ErrorAction SilentlyContinue

if ($remainingProcesses) {
    Write-Host "Warning: Some 'waitress-serve' processes are still running:"
    foreach ($process in $remainingProcesses) {
        Write-Host "PID: $($process.Id), Process Name: $($process.ProcessName)"
    }
} else {
    Write-Host "All 'waitress-serve' processes have been successfully terminated."
}