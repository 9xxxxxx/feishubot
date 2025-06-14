# CONFIGURATION
$MB_HOST = "0.0.0.0"    # 绑定地址 (默认 0.0.0.0=所有接口)
$MB_PORT = 17608         # 监听端口
$JDBC_URI = "jdbc:mysql://localhost:3306/metabase?user=root&password=000000&useSSL=false"

# JAVA OPTIONS
$JAVA_OPTS = @(
    "--add-opens", "java.base/java.nio=ALL-UNNAMED",
    "-DMB_JETTY_HOST=$MB_HOST",
    "-DMB_JETTY_PORT=$MB_PORT",
    "-DMB_DB_TYPE=mysql",
    "-Dfile.encoding=UTF-8",
    "-DMB_DB_CONNECTION_URI=`"$JDBC_URI`""
)

# REQUIREMENT CHECKS
if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
    Write-Error "Java runtime not found in PATH"
    exit 1
}

if (-not (Test-Path "metabase.jar")) {
    Write-Error "metabase.jar not found in current directory"
    exit 1
}

# PORT AVAILABILITY CHECK
try {
    $socket = New-Object System.Net.Sockets.TcpClient
    $socket.Connect($MB_HOST, $MB_PORT)
    $socket.Close()
    Write-Error "Port $MB_PORT is already in use on $MB_HOST"
    exit 1
} catch [System.Management.Automation.MethodInvocationException] {
    # Port available, continue
}
Start-Process "http://localhost:$MB_PORT"
# START METABASE
try {
    java @JAVA_OPTS -jar metabase.jar
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Metabase exited with error code $LASTEXITCODE"
    }

}
catch {
    Write-Error "Failed to start Metabase: $_"
    exit 1
}
