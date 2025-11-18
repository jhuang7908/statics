# 逐步部署指南 - 解决上传问题

## 步骤 1: 运行诊断脚本

首先运行诊断脚本，查看具体问题：

```bash
diagnose_issue.bat
```

## 步骤 2: 配置 Git（如果未配置）

如果诊断显示未配置 Git 用户信息，运行：

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 步骤 3: 确保 GitHub 仓库存在

访问并确认仓库存在：
**https://github.com/jhuang7908/statics**

如果不存在，创建仓库：
1. 访问：https://github.com/new
2. 仓库名：`statics`
3. 所有者：`jhuang7908`
4. **不要**勾选 "Initialize with README"
5. 点击 "Create repository"

## 步骤 4: 手动执行部署命令

如果脚本失败，可以手动执行：

### 4.1 初始化 Git（如果还没有）

```bash
git init
```

### 4.2 添加文件

```bash
git add .
```

### 4.3 提交更改

```bash
git commit -m "Initial commit: stat-IDE v1"
```

### 4.4 配置远程仓库

```bash
git remote add origin https://github.com/jhuang7908/statics.git
```

如果已经存在，更新地址：
```bash
git remote set-url origin https://github.com/jhuang7908/statics.git
```

### 4.5 设置主分支

```bash
git branch -M main
```

### 4.6 推送到 GitHub

```bash
git push -u origin main
```

## 步骤 5: 处理认证问题

如果 `git push` 失败，提示认证错误：

### 方案 A: 使用 Personal Access Token（推荐）

1. 生成 Token：
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token" → "Generate new token (classic)"
   - 名称：`stat-IDE-deploy`
   - 权限：勾选 `repo`（全部权限）
   - 点击 "Generate token"
   - **复制 Token**（只显示一次）

2. 推送时使用 Token：
   - 用户名：输入你的 GitHub 用户名
   - 密码：**粘贴 Token**（不是密码）

### 方案 B: 使用 SSH（如果已配置）

如果已配置 SSH key，可以改用 SSH URL：

```bash
git remote set-url origin git@github.com:jhuang7908/statics.git
git push -u origin main
```

## 步骤 6: 验证上传成功

推送成功后，访问：
**https://github.com/jhuang7908/statics**

应该能看到：
- 分支：`main`
- 文件：`app.py`, `stats_core.py`, `requirements.txt` 等

## 常见错误及解决方案

### 错误 1: "repository not found"

**原因：** 仓库不存在或没有权限

**解决：**
1. 确认仓库 URL 正确
2. 确认仓库已创建
3. 确认有访问权限

### 错误 2: "Authentication failed"

**原因：** GitHub 不再支持密码认证

**解决：** 使用 Personal Access Token（见步骤 5）

### 错误 3: "Permission denied"

**原因：** 没有仓库写入权限

**解决：**
1. 确认是仓库所有者
2. 或确认有写入权限

### 错误 4: "failed to push some refs"

**原因：** 远程仓库有本地没有的提交

**解决：**
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## 快速命令总结

```bash
# 完整部署流程
git init
git add .
git commit -m "Initial commit: stat-IDE v1"
git remote add origin https://github.com/jhuang7908/statics.git
git branch -M main
git push -u origin main
```

## 获取帮助

如果仍然失败，请提供：
1. 运行 `diagnose_issue.bat` 的输出
2. `git push` 的完整错误信息
3. 仓库是否存在：https://github.com/jhuang7908/statics

