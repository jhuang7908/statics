@echo off
chcp 65001 >nul
REM 最终修复：解决冲突、修复编码、重新推送

echo ========================================
echo 最终修复：合并冲突和编码问题
echo ========================================
echo.

echo [1/5] 设置 Git 编码为 UTF-8...
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.autocrlf true
echo 完成

echo.
echo [2/5] 解决合并冲突（使用本地版本）...
git checkout --ours README.md
git add README.md
echo 完成

echo.
echo [3/5] 添加所有文件（包括 .gitattributes）...
git add .
echo 完成

echo.
echo [4/5] 提交修复...
git commit -m "Fix: 解决合并冲突并修复中文编码问题（UTF-8）"
echo 完成

echo.
echo [5/5] 推送到 GitHub...
git push origin main

echo.
if %errorlevel% equ 0 (
    echo ========================================
    echo [成功] 修复完成并已推送！
    echo.
    echo 验证: https://github.com/jhuang7908/statics
    echo 中文应该正常显示了
    echo ========================================
) else (
    echo ========================================
    echo [失败] 推送失败
    echo 请检查错误信息
    echo ========================================
)

pause

