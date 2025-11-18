@echo off
REM 诊断部署问题的脚本

echo ========================================
echo 诊断部署问题
echo ========================================
echo.

REM 1. 检查 Git 是否安装
echo [1] 检查 Git 安装...
where git >nul 2>&1
if %errorlevel% equ 0 (
    git --version
    echo     Git 已安装
) else (
    echo     [错误] Git 未安装
    echo     请下载安装: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo.

REM 2. 检查 Git 配置
echo [2] 检查 Git 用户配置...
git config --global user.name 2>nul
if %errorlevel% equ 0 (
    echo     用户名: 
    git config --global user.name
) else (
    echo     [警告] 未配置用户名
    echo     运行: git config --global user.name "Your Name"
)
git config --global user.email 2>nul
if %errorlevel% equ 0 (
    echo     邮箱: 
    git config --global user.email
) else (
    echo     [警告] 未配置邮箱
    echo     运行: git config --global user.email "your.email@example.com"
)
echo.

REM 3. 检查 Git 仓库
echo [3] 检查 Git 仓库状态...
if exist .git (
    echo     Git 仓库已初始化
    echo.
    echo     当前分支:
    git branch 2>nul
    echo.
    echo     远程仓库配置:
    git remote -v 2>nul
    if %errorlevel% neq 0 (
        echo     [警告] 未配置远程仓库
    )
    echo.
    echo     提交历史:
    git log --oneline -3 2>nul
    if %errorlevel% neq 0 (
        echo     [警告] 没有提交记录
    )
    echo.
    echo     未提交的更改:
    git status --short 2>nul
) else (
    echo     [警告] Git 仓库未初始化
    echo     需要运行: git init
)
echo.

REM 4. 测试网络连接
echo [4] 测试 GitHub 连接...
ping -n 1 github.com >nul 2>&1
if %errorlevel% equ 0 (
    echo     GitHub 网络连接正常
) else (
    echo     [警告] 无法连接到 GitHub，请检查网络
)
echo.

REM 5. 检查仓库是否存在
echo [5] 检查目标仓库...
echo     目标仓库: https://github.com/jhuang7908/statics
echo     请手动访问上述链接确认仓库是否存在
echo.

REM 6. 提供解决方案
echo ========================================
echo 诊断结果和建议:
echo ========================================
echo.

if not exist .git (
    echo [问题] Git 仓库未初始化
    echo [解决] 运行: git init
    echo.
)

git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo [问题] 未配置远程仓库
    echo [解决] 运行: git remote add origin https://github.com/jhuang7908/statics.git
    echo.
)

git log --oneline -1 >nul 2>&1
if %errorlevel% neq 0 (
    echo [问题] 没有提交记录
    echo [解决] 运行以下命令:
    echo        git add .
    echo        git commit -m "Initial commit"
    echo.
)

echo [建议] 如果推送失败，可能的原因:
echo 1. 仓库不存在 - 先创建: https://github.com/new
echo 2. 认证失败 - 使用 Personal Access Token
echo 3. 权限不足 - 确认有仓库访问权限
echo.

echo ========================================
echo 下一步操作:
echo ========================================
echo 1. 确保仓库存在: https://github.com/jhuang7908/statics
echo 2. 配置 Git 用户信息（如果未配置）
echo 3. 运行: quick_deploy.bat
echo 4. 如果认证失败，使用 Personal Access Token
echo ========================================
echo.

pause

