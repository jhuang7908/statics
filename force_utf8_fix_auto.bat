@echo off
chcp 65001 >nul
REM 强制修复编码问题 - 自动版本（无需确认）

echo ========================================
echo 强制修复中文编码问题（自动模式）
echo ========================================
echo.

echo [1/6] 设置 Git 全局编码为 UTF-8...
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.autocrlf true
git config --global gui.encoding utf-8
echo 完成

echo.
echo [2/6] 检查当前 Git 编码配置...
git config --global --get i18n.commitencoding
git config --global --get i18n.logoutputencoding
echo.

echo [3/6] 移除所有文件的 Git 缓存...
git rm -r --cached . 2>nul
echo 完成

echo.
echo [4/6] 重新添加所有文件（使用 UTF-8）...
git add .
echo 完成

echo.
echo [5/6] 提交更改（强制 UTF-8 编码）...
git commit -m "Fix: 强制修复中文编码问题 - 使用 UTF-8 重新提交所有文件" 2>nul
if %errorlevel% neq 0 (
    echo 提示: 可能没有更改需要提交，或已有相同提交
)
echo 完成

echo.
echo [6/6] 强制推送到 GitHub（覆盖远程）...
echo 警告: 这将覆盖远程仓库的内容
echo.
git push -u origin main --force

echo.
if %errorlevel% equ 0 (
    echo ========================================
    echo [成功] 编码修复完成并已推送！
    echo.
    echo 验证: https://github.com/jhuang7908/statics
    echo 请刷新页面查看中文是否正常显示
    echo ========================================
) else (
    echo ========================================
    echo [失败] 推送失败
    echo 请检查错误信息
    echo.
    echo 可能的原因:
    echo 1. 需要 GitHub 认证（使用 Personal Access Token）
    echo 2. 网络连接问题
    echo 3. 权限不足
    echo ========================================
)

echo.
pause

