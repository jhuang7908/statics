# 在 Streamlit Cloud 上使用 AI 功能

## 问题说明

**当前情况：**
- 应用依赖本地 Ollama 服务（`http://localhost:11434`）
- Streamlit Cloud 无法访问本地服务
- AI 功能在云端无法使用

## 解决方案

### 方案 1: 配置远程 Ollama 服务（推荐）

#### 步骤 1: 部署远程 Ollama 服务

你需要在云服务器上部署 Ollama：

**选项 A: 使用云服务器（AWS、Azure、GCP 等）**

1. 在云服务器上安装 Ollama：
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. 下载模型：
   ```bash
   ollama pull phi3:mini
   ```

3. 启动 Ollama 服务（确保可以从外部访问）：
   ```bash
   # 默认端口 11434
   # 确保防火墙开放该端口
   ```

**选项 B: 使用 Docker**

```bash
docker run -d -p 11434:11434 --name ollama ollama/ollama
docker exec -it ollama ollama pull phi3:mini
```

**选项 C: 使用 Ollama 托管服务**

如果有第三方 Ollama 托管服务，使用其提供的 API 地址。

#### 步骤 2: 在 Streamlit Cloud 配置 Secrets

1. **访问 Streamlit Cloud 应用设置**
   - 打开你的应用页面
   - 点击右上角 "⋮"（三个点）菜单
   - 选择 "Settings"（设置）

2. **添加 Secrets**
   - 点击 "Secrets"（密钥）标签
   - 在编辑器中添加以下内容：

```toml
[ollama]
api_url = "https://your-ollama-server.com:11434"
# 如果需要认证，添加：
# api_key = "your-api-key"
```

**示例：**
```toml
[ollama]
api_url = "https://ollama.example.com:11434"
```

3. **保存并重新部署**
   - 点击 "Save"（保存）
   - Streamlit Cloud 会自动重新部署应用

#### 步骤 3: 验证配置

部署完成后，AI 功能应该可以正常使用。

### 方案 2: 使用其他 AI 服务（替代方案）

如果不想部署 Ollama，可以修改代码使用其他 AI 服务：

#### 选项 A: OpenAI API

修改 `ollama_client.py` 使用 OpenAI：

```python
import openai

def ask_model(prompt: str, system_prompt: str = ""):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
```

在 Streamlit Secrets 中配置：
```toml
[openai]
api_key = "your-openai-api-key"
```

#### 选项 B: Anthropic Claude API

类似地，可以使用 Claude API。

### 方案 3: 暂时禁用 AI 功能（临时方案）

如果暂时不需要 AI 功能，可以：

1. **在代码中添加错误处理**
   - 当 Ollama 连接失败时，显示友好提示
   - 其他统计功能继续正常工作

2. **隐藏 AI 聊天区域**
   - 在 Streamlit Cloud 上隐藏 AI 相关 UI

## 当前代码状态

你的 `ollama_client.py` 已经支持从 Streamlit Secrets 读取配置：

```python
def get_ollama_url():
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'ollama' in st.secrets:
            return st.secrets.ollama.get('api_url', 'http://localhost:11434')
    except:
        pass
    return os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
```

这意味着你只需要：
1. 部署远程 Ollama 服务
2. 在 Streamlit Secrets 中配置 API 地址
3. 应用会自动使用远程服务

## 快速设置步骤

### 1. 部署 Ollama 服务

选择一个云服务器，安装并运行 Ollama。

### 2. 配置 Streamlit Secrets

在 Streamlit Cloud 应用设置中添加：
```toml
[ollama]
api_url = "https://your-server-ip:11434"
```

### 3. 验证

部署后测试 AI 聊天功能是否正常。

## 安全注意事项

### ⚠️ 如果使用 HTTP（不安全）

如果 Ollama 服务使用 HTTP（非 HTTPS）：
- 数据可能被截获
- 建议使用 HTTPS 或 VPN

### 🔒 如果 Ollama 需要认证

如果远程 Ollama 服务需要认证，在 Secrets 中添加：
```toml
[ollama]
api_url = "https://your-server.com:11434"
api_key = "your-api-key"
```

然后在 `ollama_client.py` 中添加认证头。

## 故障排除

### 问题 1: 连接超时

**原因：** 服务器地址不正确或无法访问

**解决：**
- 检查服务器地址是否正确
- 确认防火墙开放了 11434 端口
- 测试从浏览器访问：`http://your-server:11434`

### 问题 2: CORS 错误

**原因：** Ollama 服务器未配置 CORS

**解决：** 在 Ollama 服务器配置中允许跨域请求

### 问题 3: 认证失败

**原因：** API key 不正确

**解决：** 检查 Secrets 中的配置是否正确

## 推荐方案

**最简单的方式：**
1. 使用云服务器（如 AWS EC2、DigitalOcean 等）
2. 安装 Ollama 并下载模型
3. 在 Streamlit Secrets 中配置服务器地址
4. 完成！

## 成本考虑

- **Ollama 自托管**：只需要云服务器费用（约 $5-20/月）
- **OpenAI API**：按使用量付费（约 $0.002/1000 tokens）
- **Claude API**：按使用量付费

## 快速链接

- **Ollama 安装指南**: https://ollama.ai/
- **Streamlit Secrets 文档**: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management

