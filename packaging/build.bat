@echo off
REM Build standalone executable using PyInstaller

IF NOT EXIST ..\.venv\Scripts\activate.bat (
    echo Virtual environment not found. Please create one in project root.
    exit /b 1
)

call ..\.venv\Scripts\activate.bat

pyinstaller --noconfirm ^
    --clean ^
    --add-data "..\phi3_stat_studio\templates;phi3_stat_studio/templates" ^
    --add-data "..\phi3_stat_studio\assets;phi3_stat_studio/assets" ^
    --name "Phi3StatStudio" ^
    --windowed ^
    ..\phi3_stat_studio\app.py

echo Build complete. Check the dist directory.


