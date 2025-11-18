@echo off
REM 部署到 GitHub 的批处理脚本
REM 目标仓库: https://github.com/jhuang7908/statics

echo ========================================
echo 部署 stat-IDE 到 GitHub
echo 目标仓库: https://github.com/jhuang7908/statics
echo ========================================
echo.

REM 检查是否已初始化 Git 仓库
if not exist .git (
    echo [1/5] 初始化 Git 仓库...
    git init
    echo Git 仓库已初始化
) else (
    echo [1/5] Git 仓库已存在
)

echo.
echo [2/5] 添加所有文件到暂存区...
git add .

echo.
echo [3/5] 提交更改...
git commit -m "Update: stat-IDE v1 - 经典统计模块"

echo.
echo [4/5] 检查远程仓库配置...
git remote -v

REM 检查是否已配置远程仓库
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo 添加远程仓库...
    git remote add origin https://github.com/jhuang7908/statics.git
    echo 远程仓库已添加: https://github.com/jhuang7908/statics.git
) else (
    REM 检查远程仓库地址是否正确
    for /f "tokens=*" %%i in ('git remote get-url origin') do set REMOTE_URL=%%i
    if not "%REMOTE_URL%"=="https://github.com/jhuang7908/statics.git" (
        echo 更新远程仓库地址...
        git remote set-url origin https://github.com/jhuang7908/statics.git
        echo 远程仓库地址已更新
    ) else (
        echo 远程仓库地址正确
    )
)

echo.
echo [5/5] 推送到 GitHub...
git branch -M main
git push -u origin main

echo.
echo ========================================
if %errorlevel% equ 0 (
    echo 部署成功！
    echo 仓库地址: https://github.com/jhuang7908/statics
    echo.
    echo 下一步: 在 Streamlit Community Cloud 部署
    echo 1. 访问 https://share.streamlit.io/
    echo 2. 使用 GitHub 账号登录
    echo 3. 选择仓库: jhuang7908/statics
    echo 4. 主文件: app.py
    echo 5. 点击 Deploy
) else (
    echo 部署失败，请检查错误信息
    echo 可能的原因:
    echo - GitHub 仓库不存在或没有权限
    echo - 需要先创建仓库: https://github.com/jhuang7908/statics
    echo - 需要配置 GitHub 认证
)
echo ========================================
pause

