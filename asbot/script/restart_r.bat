@echo off
echo ==========================================
echo Task start time: %date% %time%
echo ==========================================

:: Terminate specific R script instance
echo [1/2] Terminating R script instance...
taskkill /FI "IMAGENAME eq Rscript.exe" /FI "COMMANDLINE eq E:\Dev\AS_Bot\asbot\app.R" /F

if %ERRORLEVEL% equ 0 (
    echo R script instance terminated successfully.
) else (
    echo No R script instance found, or termination failed.
)

:: Restart R script
echo [2/2] Restarting R script...
Rscript E:\Dev\LH_Bi\app.R >> E:\Dev\LH_Bi\restart_r.log 2>&1

if %ERRORLEVEL% equ 0 (
    echo R script started successfully.
) else (
    echo R script failed to start, please check the log file.
)

echo ==========================================
echo Task end time: %date% %time%
echo ==========================================
