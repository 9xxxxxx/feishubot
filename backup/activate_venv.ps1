Write-Host "Activating Conda environment..."
conda activate superset

if (-not $?) {
    Write-Host "Failed to activate Conda environment."
    exit 1
}

Write-Host "Current environment: $env:CONDA_DEFAULT_ENV"

Write-Host "Setting environment variables..."
$env:FLASK_APP = "superset"
$env:SUPERSET_CONFIG_PATH = "C:\Users\garry\anaconda3\envs\superset\Lib\site-packages\superset\superset_config.py"

Write-Host "FLASK_APP: $env:FLASK_APP"
Write-Host "SUPERSET_CONFIG_PATH: $env:SUPERSET_CONFIG_PATH"

Write-Host "environment variables import success"
