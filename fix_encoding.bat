@echo off
chcp 65001 >nul
REM 修复编码问题的脚本
REM 设置代码页为 UTF-8

echo ========================================
echo 修复编码问题
echo ========================================
echo.

echo [1] 设置 Git 编码为 UTF-8...
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8

echo [2] 设置 Git 自动转换换行符...
git config --global core.autocrlf true

echo [3] 检查当前 Git 配置...
echo.
echo Git 用户配置:
git config --global user.name
git config --global user.email
echo.
echo Git 编码配置:
git config --global i18n.commitencoding
git config --global i18n.logoutputencoding

echo.
echo ========================================
echo 编码修复完成
echo ========================================
echo.
echo 注意: 批处理文件应保存为 UTF-8 编码
echo 如果仍有乱码，请检查文件编码
echo.

pause

