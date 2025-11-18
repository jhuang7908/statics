@echo off
chcp 65001 >nul
REM 转换文件编码为 UTF-8（使用 Python）

echo ========================================
echo 转换文件编码为 UTF-8
echo ========================================
echo.

echo [1/3] 检查 Python 是否安装...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Python 未安装
    echo 请先安装 Python: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Python 已安装

echo.
echo [2/3] 安装 chardet（如果需要）...
pip install chardet >nul 2>&1

echo.
echo [3/3] 检查文件编码...
python check_file_encoding.py

echo.
echo ========================================
echo 如果文件不是 UTF-8 编码，请：
echo 1. 在编辑器中打开文件
echo 2. 另存为 UTF-8 编码
echo 3. 然后运行: force_utf8_fix.bat
echo ========================================
echo.

pause

