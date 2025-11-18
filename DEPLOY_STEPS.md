# 部署到 GitHub 和 Streamlit Cloud 步骤

## 目标仓库
**GitHub 仓库地址：** https://github.com/jhuang7908/statics

## 快速部署（使用批处理脚本）

### Windows 用户
直接运行：
```bash
deploy_to_github.bat
```

## 手动部署步骤

### 1. 确保 GitHub 仓库已创建

如果仓库还不存在，请先创建：
1. 访问 https://github.com/jhuang7908
2. 点击 "New repository" 或 "新建仓库"
3. 仓库名称：`statics`
4. 选择 Public（公开）或 Private（私有）
5. **不要**勾选 "Initialize this repository with a README"（本地已有代码）
6. 点击 "Create repository"

### 2. 初始化 Git 仓库（如果还没有）

```bash
# 检查是否已初始化
git status

# 如果没有初始化，执行：
git init
```

### 3. 添加并提交文件

```bash
# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit: stat-IDE v1 - 经典统计模块"
```

### 4. 连接远程仓库并推送

```bash
# 添加远程仓库
git remote add origin https://github.com/jhuang7908/statics.git

# 如果已经添加过，更新地址：
# git remote set-url origin https://github.com/jhuang7908/statics.git

# 设置主分支
git branch -M main

# 推送到 GitHub
git push -u origin main
```

**注意：** 如果是第一次推送，可能需要：
- 配置 GitHub 认证（Personal Access Token 或 SSH key）
- 输入 GitHub 用户名和密码/Token

### 5. 验证推送成功

访问 https://github.com/jhuang7908/statics 查看代码是否已上传。

## 部署到 Streamlit Community Cloud

### 步骤 1: 访问 Streamlit Cloud
- 打开 https://share.streamlit.io/
- 或访问 https://streamlit.io/cloud

### 步骤 2: 登录
- 点击 "Sign in"
- 使用 GitHub 账号登录（授权 Streamlit 访问）

### 步骤 3: 部署应用
1. 点击 "New app" 或 "新建应用"
2. **Repository（仓库）**: 选择 `jhuang7908/statics`
3. **Branch（分支）**: 选择 `main` 或 `master`
4. **Main file path（主文件路径）**: 输入 `app.py`
5. **App URL（应用URL，可选）**: 可以自定义，如 `stat-ide`
6. 点击 "Deploy" 或 "部署"

### 步骤 4: 等待部署完成
- Streamlit 会自动安装依赖（从 `requirements.txt`）
- 部署完成后，你会获得一个 URL，如：
  - `https://stat-ide.streamlit.app`
  - 或 `https://share.streamlit.io/jhuang7908/statics`

## 更新应用

每次修改代码后，只需：

```bash
git add .
git commit -m "Update: 描述你的更改"
git push origin main
```

Streamlit Cloud 会自动检测到更改并重新部署（通常需要几分钟）。

## 配置 Ollama（可选）

如果需要在云端使用 AI 功能：

1. 在 Streamlit Cloud 应用页面，点击 "Settings"（设置）
2. 选择 "Secrets"（密钥）
3. 添加以下内容：

```toml
[ollama]
api_url = "https://your-ollama-server.com:11434"
```

4. 保存后，应用会自动重新部署

**注意：** 如果没有配置远程 Ollama 服务，AI 功能将无法使用，但其他统计功能可以正常使用。

## 故障排除

### 问题 1: 推送失败 - 认证错误
**解决方案：**
- 使用 Personal Access Token 代替密码
- 或配置 SSH key

### 问题 2: 仓库不存在
**解决方案：**
- 先在 GitHub 上创建仓库：https://github.com/new
- 仓库名：`statics`
- 所有者：`jhuang7908`

### 问题 3: 部署失败 - 找不到依赖
**解决方案：**
- 检查 `requirements.txt` 是否包含所有依赖
- 确保版本号兼容

### 问题 4: 应用无法启动
**解决方案：**
- 查看 Streamlit Cloud 的日志
- 检查 `app.py` 是否有语法错误
- 确保所有导入的模块都在 `requirements.txt` 中

## 快速命令参考

```bash
# 初始化（如果需要）
git init
git add .
git commit -m "Initial commit"

# 连接 GitHub
git remote add origin https://github.com/jhuang7908/statics.git
git branch -M main
git push -u origin main

# 更新代码
git add .
git commit -m "Update message"
git push origin main
```

