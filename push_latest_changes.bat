@echo off
chcp 65001 >nul
REM 推送最新更改到 GitHub

echo ========================================
echo 推送最新更改到 GitHub
echo ========================================
echo.

REM 检查 Git 是否安装
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Git 未安装
    echo 下载: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/5] 检查 Git 仓库状态...
git status
echo.

echo [2/5] 检查远程仓库配置...
git remote -v
echo.

echo [3/5] 添加所有更改的文件...
git add .
echo 完成
echo.

echo [4/5] 提交更改...
git commit -m "Update: 修复图形中文字体显示和AI功能提示优化"
echo 完成
echo.

echo [5/5] 推送到 GitHub...
git push origin main

echo.
if %errorlevel% equ 0 (
    echo ========================================
    echo [成功] 已推送到 GitHub！
    echo.
    echo 仓库: https://github.com/jhuang7908/statics
    echo 分支: main
    echo ========================================
) else (
    echo ========================================
    echo [失败] 推送失败
    echo.
    echo 可能的原因:
    echo 1. 需要 GitHub 认证（使用 Personal Access Token）
    echo 2. 网络连接问题
    echo 3. 权限不足
    echo.
    echo 如果认证失败，请使用 Personal Access Token
    echo 生成 Token: https://github.com/settings/tokens
    echo ========================================
)

echo.
pause

