# 检查 Git 仓库和上传状态的 PowerShell 脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "检查 Git 仓库和上传状态" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Git 是否安装
try {
    $gitVersion = git --version 2>&1
    Write-Host "[✓] Git 已安装: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] Git 未安装或不在 PATH 中" -ForegroundColor Red
    Write-Host "请先安装 Git: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# 检查 Git 仓库
if (Test-Path .git) {
    Write-Host "[1] Git 仓库状态: 已初始化" -ForegroundColor Green
    Write-Host ""
    
    # 检查远程仓库
    Write-Host "[2] 远程仓库配置:" -ForegroundColor Cyan
    try {
        $remotes = git remote -v 2>&1
        if ($remotes) {
            Write-Host $remotes
        } else {
            Write-Host "  未配置远程仓库" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  无法获取远程仓库信息" -ForegroundColor Red
    }
    Write-Host ""
    
    # 检查提交历史
    Write-Host "[3] 最近的提交历史:" -ForegroundColor Cyan
    try {
        $log = git log --oneline -5 2>&1
        if ($log) {
            Write-Host $log
        } else {
            Write-Host "  暂无提交记录" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  无法获取提交历史" -ForegroundColor Red
    }
    Write-Host ""
    
    # 检查未提交的更改
    Write-Host "[4] 未提交的更改:" -ForegroundColor Cyan
    try {
        $status = git status --short 2>&1
        if ($status) {
            Write-Host $status
        } else {
            Write-Host "  工作区干净，无未提交更改" -ForegroundColor Green
        }
    } catch {
        Write-Host "  无法获取状态" -ForegroundColor Red
    }
    Write-Host ""
    
    # 检查远程分支
    Write-Host "[5] 远程分支:" -ForegroundColor Cyan
    try {
        $branches = git branch -r 2>&1
        if ($branches) {
            Write-Host $branches
        } else {
            Write-Host "  未找到远程分支" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  无法获取远程分支" -ForegroundColor Red
    }
    Write-Host ""
    
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "验证上传状态:" -ForegroundColor Yellow
    Write-Host "1. 如果看到 'origin' 远程仓库指向 github.com/jhuang7908/statics，说明已配置" -ForegroundColor White
    Write-Host "2. 如果看到提交历史，说明有提交记录" -ForegroundColor White
    Write-Host "3. 访问 https://github.com/jhuang7908/statics 查看是否已上传" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Cyan
    
} else {
    Write-Host "[1] Git 仓库状态: 未初始化" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "[提示] 需要先初始化 Git 仓库" -ForegroundColor Yellow
    Write-Host "运行: .\deploy_to_github.bat" -ForegroundColor Cyan
    Write-Host "或运行: .\deploy_to_github.bat" -ForegroundColor Cyan
}

Write-Host ""
Read-Host "按 Enter 键退出"

