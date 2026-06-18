@echo off
echo === ASMRify Build Script ===
echo.

REM Check that assets\icon.ico exists
if not exist "assets\icon.ico" (
    echo ERROR: assets\icon.ico not found. Cannot build.
    pause
    exit /b 1
)

REM Clean previous build artifacts
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

REM Build the exe
pyinstaller --onedir --windowed ^
  --icon "assets\icon.ico" ^
  --add-data "assets\icon.ico;." ^
  --name "ASMRifier" ^
  main.py

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller failed. See output above.
    pause
    exit /b 1
)

REM Create release folder
if exist "release\ASMRifier" rmdir /s /q "release\ASMRifier"
mkdir "release\ASMRifier"

REM Copy compiled app
xcopy /E /I /Y "dist\ASMRifier" "release\ASMRifier"

REM Copy release documents
copy /Y README.md "release\ASMRifier\"
copy /Y promo.md  "release\ASMRifier\"
copy /Y guide.md  "release\ASMRifier\"

REM Copy promo screenshots if folder is non-empty
if exist promo (
    xcopy /E /I /Y promo "release\ASMRifier\promo"
)

REM Clean PyInstaller working dirs
rmdir /s /q build
rmdir /s /q dist

echo.
echo === Build complete ===
echo Release folder: release\ASMRifier\
echo Zip that folder and upload to itch.io.
pause
