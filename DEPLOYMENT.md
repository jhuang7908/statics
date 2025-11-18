# Streamlit Community Cloud 部署指南

## 前置条件

1. 拥有 GitHub 账号
2. 已安装 Git
3. 代码已准备好

## 部署步骤

### 1. 初始化 Git 仓库（如果还没有）

```bash
# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit: stat-IDE v1"
```

### 2. 创建 GitHub 仓库

1. 访问 [GitHub](https://github.com)
2. 点击右上角的 "+" → "New repository"
3. 填写仓库信息：
   - Repository name: `stat-IDE` (或你喜欢的名字)
   - Description: `AI辅助Python编程的统计工具`
   - 选择 Public（公开）或 Private（私有）
   - **不要**勾选 "Initialize this repository with a README"（因为本地已有代码）
4. 点击 "Create repository"

### 3. 连接本地仓库到 GitHub

```bash
# 添加远程仓库（将 YOUR_USERNAME 和 YOUR_REPO 替换为你的实际信息）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 或者使用 SSH（如果你配置了 SSH key）
# git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git

# 推送代码到 GitHub
git branch -M main
git push -u origin main
```

### 4. 部署到 Streamlit Community Cloud

1. **访问 Streamlit Community Cloud**
   - 打开 [https://share.streamlit.io/](https://share.streamlit.io/)
   - 或访问 [https://streamlit.io/cloud](https://streamlit.io/cloud)

2. **登录**
   - 点击 "Sign in"
   - 使用 GitHub 账号登录（授权 Streamlit 访问你的 GitHub）

3. **部署应用**
   - 点击 "New app"
   - 选择你的 GitHub 仓库
   - 选择分支（通常是 `main` 或 `master`）
   - 设置主文件路径：`app.py`
   - 点击 "Deploy"

4. **等待部署完成**
   - Streamlit 会自动安装依赖（从 `requirements.txt`）
   - 部署完成后，你会获得一个公开的 URL（如：`https://your-app-name.streamlit.app`）

### 5. 更新应用

每次更新代码后，只需推送到 GitHub：

```bash
git add .
git commit -m "Update: 描述你的更改"
git push origin main
```

Streamlit Community Cloud 会自动检测到更改并重新部署。

## 重要注意事项

### ⚠️ Ollama AI 功能限制

**当前问题：** 应用依赖本地 Ollama 服务（`http://localhost:11434`），部署到云端后无法访问本地服务。

**解决方案：**

1. **禁用 AI 功能（临时方案）**
   - 在云端部署时，AI 聊天功能将无法使用
   - 其他统计功能可以正常使用

2. **配置远程 Ollama 服务（推荐）**
   - 在云服务器上部署 Ollama
   - 修改 `ollama_client.py` 中的 API 地址
   - 使用环境变量配置 API 地址

3. **使用 Streamlit 的 Secrets 管理**
   - 在 Streamlit Cloud 中配置 Secrets
   - 存储 Ollama 服务的远程地址和认证信息

### 📝 环境变量配置（可选）

如果需要配置远程 Ollama 服务，可以在 Streamlit Cloud 的 "Settings" → "Secrets" 中添加：

```toml
[ollama]
api_url = "https://your-ollama-server.com:11434"
api_key = "your-api-key-if-needed"
```

然后在 `ollama_client.py` 中读取：

```python
import os
import streamlit as st

# 从 Streamlit Secrets 或环境变量读取
ollama_url = st.secrets.get("ollama", {}).get("api_url", "http://localhost:11434")
```

### 📦 依赖检查

确保 `requirements.txt` 包含所有必需的依赖：

```txt
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.23.0
scipy>=1.9.0
statsmodels>=0.13.0
matplotlib>=3.6.0
seaborn>=0.12.0
requests>=2.28.0
reportlab>=4.0.0
```

### 🔒 数据隐私

- Streamlit Community Cloud 的应用是**公开的**
- 所有上传的数据对所有访问者可见
- **请勿上传敏感数据**
- 建议在应用首页添加数据隐私提示

## 故障排除

### 问题 1: 部署失败 - 找不到依赖

**解决方案：** 检查 `requirements.txt` 是否包含所有依赖，版本号是否兼容。

### 问题 2: 应用无法启动

**解决方案：** 
- 检查 `app.py` 是否有语法错误
- 查看 Streamlit Cloud 的日志（在应用设置中）
- 确保所有导入的模块都在 `requirements.txt` 中

### 问题 3: AI 功能不工作

**解决方案：** 
- 这是预期的，因为 Ollama 在本地运行
- 需要配置远程 Ollama 服务或暂时禁用 AI 功能

### 问题 4: 中文显示问题

**解决方案：** 
- 确保 PDF 生成功能中的中文字体注册代码正确
- 在云端环境中，可能需要使用不同的字体路径

## 快速命令参考

```bash
# 初始化仓库
git init
git add .
git commit -m "Initial commit"

# 连接 GitHub
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main

# 更新代码
git add .
git commit -m "Update message"
git push origin main
```

## 下一步

部署成功后，你可以：
1. 分享应用 URL 给其他人使用
2. 在 README 中添加部署链接
3. 继续开发新功能并自动部署

