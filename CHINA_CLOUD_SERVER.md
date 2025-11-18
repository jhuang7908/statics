# 中国云服务器获取指南

## 国内主要云服务提供商

### 1. 阿里云（推荐）

**优点：**
- 国内访问速度快
- 中文界面，操作简单
- 价格相对便宜
- 新用户有优惠

**注册：**
- 网站：https://www.aliyun.com/
- 新用户通常有优惠券

**价格：**
- 轻量应用服务器：约 ¥24/月起
- ECS 云服务器：约 ¥50/月起

### 2. 腾讯云

**优点：**
- 国内服务稳定
- 中文界面
- 新用户有优惠

**注册：**
- 网站：https://cloud.tencent.com/
- 新用户有免费试用

**价格：**
- 轻量应用服务器：约 ¥24/月起
- CVM 云服务器：约 ¥50/月起

### 3. 华为云

**优点：**
- 企业级服务
- 国内访问快

**注册：**
- 网站：https://www.huaweicloud.com/

### 4. 百度云

**优点：**
- 价格便宜
- 适合小型项目

**注册：**
- 网站：https://cloud.baidu.com/

## 推荐方案：阿里云轻量应用服务器

### 步骤 1: 注册阿里云账号

1. 访问：https://www.aliyun.com/
2. 点击 "免费注册"
3. 完成实名认证（需要身份证）
4. 新用户通常有优惠券

### 步骤 2: 购买轻量应用服务器

1. 登录阿里云控制台
2. 搜索 "轻量应用服务器" 或访问：https://ecs.console.aliyun.com/
3. 点击 "创建实例"
4. 选择配置：
   - **地域**：选择离你最近的（如：华东1-杭州）
   - **镜像**：Ubuntu 22.04 或 CentOS 7
   - **套餐**：选择最便宜的（通常 ¥24/月，1核1GB）
   - **购买时长**：1个月（可以先试用）
5. 设置：
   - **实例名称**：stat-ide-ollama（自定义）
   - **密码**：设置 root 密码（记住这个密码）
6. 点击 "立即购买" 并支付

### 步骤 3: 配置安全组（重要！）

1. 在控制台找到你的服务器实例
2. 点击实例名称进入详情
3. 点击 "防火墙" 或 "安全组"
4. 添加规则：
   - **端口范围**：11434
   - **协议**：TCP
   - **授权对象**：0.0.0.0/0（允许所有IP，或只允许 Streamlit Cloud IP）
   - **描述**：Ollama API
5. 保存规则

### 步骤 4: 连接到服务器

**获取服务器 IP：**
- 在控制台可以看到公网 IP，例如：`47.xxx.xxx.xxx`

**Windows 用户连接：**
- 使用 PuTTY：https://www.putty.org/
- 或使用 PowerShell：

```powershell
ssh root@your-server-ip
# 输入密码（购买时设置的）
```

**Mac/Linux 用户：**
```bash
ssh root@your-server-ip
# 输入密码
```

### 步骤 5: 安装 Ollama

连接到服务器后，运行：

```bash
# 更新系统
apt update && apt upgrade -y

# 安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull phi3:mini

# 启动服务（确保在后台运行）
nohup ollama serve > /dev/null 2>&1 &

# 检查服务是否运行
curl http://localhost:11434/api/tags
```

### 步骤 6: 测试服务

在浏览器中访问（替换为你的服务器 IP）：
```
http://your-server-ip:11434
```

或使用 curl 测试：
```bash
curl http://your-server-ip:11434/api/tags
```

### 步骤 7: 在 Streamlit Cloud 配置

1. 访问你的 Streamlit Cloud 应用
2. 点击 "Settings" → "Secrets"
3. 添加：

```toml
[ollama]
api_url = "http://your-server-ip:11434"
```

**示例：**
```toml
[ollama]
api_url = "http://47.xxx.xxx.xxx:11434"
```

4. 保存并等待重新部署

## 腾讯云部署步骤

### 步骤 1: 注册并购买

1. 访问：https://cloud.tencent.com/
2. 注册账号并实名认证
3. 进入 "轻量应用服务器" 控制台
4. 点击 "新建"
5. 选择：
   - **地域**：选择最近的
   - **镜像**：Ubuntu 22.04
   - **套餐**：最便宜的（约 ¥24/月）
6. 设置密码并购买

### 步骤 2: 配置防火墙

1. 在控制台找到服务器
2. 点击 "防火墙" 标签
3. 添加规则：
   - **端口**：11434
   - **协议**：TCP
   - **策略**：允许
4. 保存

### 步骤 3: 安装 Ollama

同阿里云步骤 5

## 使用 Docker 部署（更简单）

如果你熟悉 Docker，可以更简单地部署：

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 启动 Docker 服务
systemctl start docker
systemctl enable docker

# 运行 Ollama 容器
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama

# 下载模型
docker exec -it ollama ollama pull phi3:mini

# 检查服务
curl http://localhost:11434/api/tags
```

## 成本对比（国内）

| 服务商 | 最低价格 | 配置 | 适合场景 |
|--------|---------|------|----------|
| **阿里云** | **¥24/月** | **1核1GB** | **推荐** |
| 腾讯云 | ¥24/月 | 1核1GB | 推荐 |
| 华为云 | ¥50/月 | 1核1GB | 企业用户 |
| 百度云 | ¥30/月 | 1核1GB | 备选 |

## 注意事项

### ⚠️ 实名认证

- 所有国内云服务商都需要实名认证
- 需要提供身份证信息
- 认证通常需要几分钟到几小时

### 🔒 安全配置

1. **修改默认密码**：购买后立即修改 root 密码
2. **配置防火墙**：只开放必要端口（11434）
3. **使用密钥对**：建议使用 SSH 密钥而非密码

### 📊 性能考虑

- **1GB RAM**：可以运行 phi3:mini，但可能较慢
- **2GB RAM**：推荐配置，运行更流畅
- **4GB RAM**：如果预算允许，性能更好

## 免费试用选项

### 阿里云
- 新用户通常有 ¥100-300 代金券
- 可以免费试用 1-3 个月

### 腾讯云
- 新用户有免费试用套餐
- 通常 1-3 个月免费

## 快速命令参考

### 连接服务器
```bash
ssh root@your-server-ip
```

### 安装 Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull phi3:mini
nohup ollama serve > /dev/null 2>&1 &
```

### 检查服务
```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 检查端口是否开放
netstat -tlnp | grep 11434
```

### 查看日志
```bash
# 查看 Ollama 日志
journalctl -u ollama -f
```

## 故障排除

### 问题 1: 无法连接服务器

**解决：**
- 检查安全组是否开放 22 端口（SSH）
- 确认 IP 地址正确
- 检查密码是否正确

### 问题 2: Ollama 无法从外部访问

**解决：**
- 检查安全组是否开放 11434 端口
- 检查防火墙规则
- 确认 Ollama 服务正在运行

### 问题 3: 内存不足

**解决：**
- phi3:mini 需要至少 1GB RAM
- 如果只有 1GB，可能需要升级到 2GB
- 或关闭其他不必要的服务

## 推荐流程

1. **注册阿里云账号**（最简单，中文界面）
2. **购买轻量应用服务器**（¥24/月，1核1GB）
3. **配置安全组**（开放 11434 端口）
4. **安装 Ollama**（按照上面的命令）
5. **在 Streamlit Cloud 配置 Secrets**
6. **完成！**

## 快速链接

- **阿里云**: https://www.aliyun.com/
- **腾讯云**: https://cloud.tencent.com/
- **华为云**: https://www.huaweicloud.com/
- **百度云**: https://cloud.baidu.com/

## 下一步

选择云服务商后，按照上面的步骤：
1. 注册并购买服务器
2. 配置安全组
3. 安装 Ollama
4. 在 Streamlit Cloud 配置
5. 测试 AI 功能

