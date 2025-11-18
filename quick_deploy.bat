@echo off
REM 快速部署脚本 - 简化版本
REM 目标: https://github.com/jhuang7908/statics (main 分支)

echo ========================================
echo 快速部署到 GitHub
echo 仓库: jhuang7908/statics
echo 分支: main
echo ========================================
echo.

REM 检查 Git
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Git 未安装
    echo 下载: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM 初始化（如果需要）
if not exist .git (
    echo [1/4] 初始化 Git 仓库...
    git init
)

REM 添加文件
echo [2/4] 添加文件到暂存区...
git add .

REM 提交
echo [3/4] 提交更改...
git commit -m "Update: stat-IDE v1 - 经典统计模块" 2>nul
if %errorlevel% neq 0 (
    echo 提示: 可能是首次提交或没有更改
    git commit -m "Initial commit: stat-IDE v1" 2>nul
)

REM 配置远程仓库
echo [4/4] 配置远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/jhuang7908/statics.git

REM 推送到 main 分支
echo.
echo 推送到 GitHub (main 分支)...
echo 注意: 可能需要输入 GitHub 用户名和密码/Token
echo.
git branch -M main
git push -u origin main

echo.
if %errorlevel% equ 0 (
    echo ========================================
    echo [成功] 已推送到 main 分支！
    echo.
    echo 验证: https://github.com/jhuang7908/statics
    echo 分支: main
    echo ========================================
) else (
    echo ========================================
    echo [失败] 推送失败
    echo.
    echo 请检查:
    echo 1. 仓库是否存在: https://github.com/jhuang7908/statics
    echo 2. 是否有访问权限
    echo 3. GitHub 认证是否正确
    echo.
    echo 如果仓库不存在，请先创建:
    echo https://github.com/new
    echo 仓库名: statics
    echo ========================================
)

pause

