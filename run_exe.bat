@echo off
cd /d "%~dp0"
echo Запуск balloon_calculator.exe...
echo.
dist\balloon_calculator.exe
if errorlevel 1 (
    echo.
    echo ========================================
    echo ПРОГРАМА ЗАКРИЛАСЬ З ПОМИЛКОЮ
    echo ========================================
    pause
)
