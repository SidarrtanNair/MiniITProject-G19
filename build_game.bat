@echo off
REM 
echo Cleaning old build...
rmdir /s /q build
rmdir /s /q dist
del /q main.spec

REM
echo Building exe with PyInstaller...
python -m PyInstaller --onefile main.py --add-data "PlayerMovementPhysics\spritesheet.py;PlayerMovementPhysics"

REM 
echo Copying assets...
xcopy /E /I /Y Map dist\Map
xcopy /E /I /Y PlayerMovementPhysics dist\PlayerMovementPhysics

echo.
echo ========================================
echo ✅ Build complete! Find your game here:
echo dist\main.exe
echo ========================================
pause
