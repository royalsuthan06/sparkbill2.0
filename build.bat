@echo off
echo Cleaning build directories...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Building ArunCrackers standalone executable...
call .venv\Scripts\pyinstaller --noconfirm ArunCrackers.spec

echo Copying .config file for network share support...
copy ArunCrackers.exe.config dist\ArunCrackers\ArunCrackers.exe.config

echo Build completed successfully and placed in dist/ArunCrackers!
