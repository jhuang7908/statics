@echo off
chcp 65001 >nul
REM 修复合并冲突和编码问题

echo ========================================
echo 修复合并冲突和编码问题
echo ========================================
echo.

echo [1/4] 设置 Git 编码为 UTF-8...
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.autocrlf true

echo.
echo [2/4] 解决 README.md 合并冲突...
echo 将使用本地版本（保留完整内容）
echo.

REM 检查是否有冲突标记
findstr /C:"<<<<<<< HEAD" README.md >nul 2>&1
if %errorlevel% equ 0 (
    echo 发现合并冲突，正在解决...
    REM 这里需要手动编辑 README.md 或使用 Git 工具
    echo 请手动编辑 README.md，删除冲突标记（<<<<<<< HEAD, =======, >>>>>>>）
    echo 保留本地版本的内容
    echo.
    echo 或者运行: git checkout --ours README.md
    echo 然后: git add README.md
    pause
)

echo.
echo [3/4] 添加所有文件（包括 .gitattributes）...
git add .

echo.
echo [4/4] 提交修复...
git commit -m "Fix: 解决合并冲突并修复中文编码问题"

echo.
echo ========================================
echo 修复完成！
echo.
echo 下一步: 推送到 GitHub
echo 运行: git push origin main
echo ========================================
echo.

pause

