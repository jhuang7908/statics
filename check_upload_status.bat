@echo off
REM 检查上传状态的脚本

echo ========================================
echo 检查 Git 仓库和上传状态
echo ========================================
echo.

REM 检查 Git 是否安装
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Git 未安装或不在 PATH 中
    echo 请先安装 Git: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1] 检查 Git 仓库状态...
if exist .git (
    echo     Git 仓库已初始化
    echo.
    echo [2] 检查远程仓库配置...
    git remote -v
    echo.
    echo [3] 检查提交历史...
    git log --oneline -5
    echo.
    echo [4] 检查未提交的更改...
    git status --short
    echo.
    echo [5] 检查远程分支状态...
    git branch -r 2>nul
    echo.
    echo ========================================
    echo 验证上传状态：
    echo 1. 如果看到 "origin" 远程仓库，说明已配置
    echo 2. 如果看到提交历史，说明有提交记录
    echo 3. 访问 https://github.com/jhuang7908/statics 查看是否已上传
    echo ========================================
) else (
    echo     Git 仓库未初始化
    echo.
    echo [提示] 需要先初始化 Git 仓库
    echo 运行: deploy_to_github.bat
)

echo.
pause

