@echo off
chcp 65001 >nul
REM 修复推送冲突并部署
REM 设置代码页为 UTF-8 以正确显示中文

echo ========================================
echo 修复推送冲突并部署
echo ========================================
echo.

echo [问题] 远程仓库包含本地没有的提交
echo [解决] 先拉取远程更改，然后合并推送
echo.

REM 确保在正确的分支
git branch -M main 2>nul

REM 拉取远程更改
echo [1/3] 拉取远程更改...
git pull origin main --allow-unrelated-histories --no-edit

if %errorlevel% equ 0 (
    echo 拉取成功
) else (
    echo [警告] 拉取时可能有冲突
    echo 将尝试强制推送（会覆盖远程内容）
    echo.
    choice /C YN /M "是否强制推送（会覆盖远程内容）"
    if errorlevel 2 goto :skip_force
    if errorlevel 1 goto :force_push
)

:force_push
echo.
echo [2/3] 强制推送到远程仓库...
echo 警告: 这将覆盖远程仓库的内容
git push -u origin main --force
goto :end

:skip_force
echo.
echo [取消] 已取消强制推送
echo 请手动解决冲突后再次推送
goto :end

:normal_push
echo.
echo [2/3] 推送到远程仓库...
git push -u origin main

:end
echo.
if %errorlevel% equ 0 (
    echo ========================================
    echo [成功] 部署完成！
    echo.
    echo 验证: https://github.com/jhuang7908/statics
    echo 分支: main
    echo ========================================
) else (
    echo ========================================
    echo [失败] 推送失败
    echo.
    echo 如果仍有问题，可以尝试:
    echo 1. 手动解决冲突后推送
    echo 2. 如果远程内容不重要，强制推送:
    echo    git push -u origin main --force
    echo ========================================
)

pause

