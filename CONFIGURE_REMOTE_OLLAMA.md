# 配置远程 Ollama 服务

## 1. 确保服务器上的 Ollama 服务持续运行

### 方法 A：使用 systemd 服务（推荐）

在服务器上创建 systemd 服务文件：

```bash
sudo nano /etc/systemd/system/ollama.service
```

添加以下内容：

```ini
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=ubuntu
Environment="OLLAMA_HOST=0.0.0.0:11434"
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

然后启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
sudo systemctl status ollama
```

### 方法 B：使用 screen（简单但需要手动管理）

```bash
screen -S ollama
ollama serve
# 按 Ctrl+A 然后按 D 退出 screen，服务继续运行
# 重新连接：screen -r ollama
```

## 2. 配置服务器安全组（腾讯云）

1. 登录腾讯云控制台
2. 进入 **云服务器 CVM** → **安全组**
3. 找到你的服务器对应的安全组
4. 点击 **入站规则** → **添加规则**
5. 添加以下规则：
   - **类型**：自定义
   - **来源**：0.0.0.0/0（或限制为 Streamlit Cloud 的 IP 范围）
   - **协议端口**：TCP:11434
   - **策略**：允许
   - **备注**：Ollama API

## 3. 配置 Streamlit 应用

### 方法 A：使用 Streamlit Secrets（推荐，用于 Streamlit Cloud）

在 Streamlit Cloud 的 **Settings** → **Secrets** 中添加：

```toml
[ollama]
api_url = "http://175.27.165.207:11434"
```

### 方法 B：使用环境变量（本地测试）

在运行 Streamlit 应用前设置：

```bash
# Windows PowerShell
$env:OLLAMA_API_URL = "http://175.27.165.207:11434"
streamlit run app.py

# Linux/Mac
export OLLAMA_API_URL="http://175.27.165.207:11434"
streamlit run app.py
```

## 4. 测试连接

在服务器上测试 Ollama 是否可以从外部访问：

```bash
# 在服务器上检查服务是否监听在 0.0.0.0:11434
sudo netstat -tlnp | grep 11434
# 或
sudo ss -tlnp | grep 11434
```

从本地测试（在 Windows PowerShell 中）：

```powershell
curl http://175.27.165.207:11434/api/tags
```

如果返回模型列表的 JSON，说明连接成功。

## 5. 验证模型可用

在服务器上确认 tinyllama 模型可用：

```bash
ollama list
ollama run tinyllama "你好"
```

## 注意事项

1. **安全性**：当前配置允许任何 IP 访问 Ollama API。建议：
   - 限制安全组规则，只允许 Streamlit Cloud 的 IP 范围
   - 或使用 VPN/内网访问
   - 或添加身份验证（需要修改 Ollama 配置）

2. **性能**：tinyllama 模型较小，响应速度较快，但能力有限。如需更好的效果，建议：
   - 升级服务器内存到 4GB 或 8GB
   - 使用更大的模型（如 phi3:mini）

3. **稳定性**：使用 systemd 服务可以确保 Ollama 在服务器重启后自动启动。

