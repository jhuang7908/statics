# 云服务器获取指南

## 主要云服务提供商

### 1. DigitalOcean（推荐新手）

**优点：**
- 简单易用，界面友好
- 价格透明，$6/月起
- 适合小型项目

**注册：**
- 网站：https://www.digitalocean.com/
- 新用户通常有 $200 免费额度（60天）

**快速开始：**
1. 注册账号
2. 创建 Droplet（选择 Ubuntu 22.04）
3. 选择最便宜的配置（$6/月，1GB RAM）
4. 创建后获得 IP 地址

### 2. AWS（Amazon Web Services）

**优点：**
- 全球最大的云服务商
- 功能强大，资源丰富
- 有免费套餐（12个月）

**注册：**
- 网站：https://aws.amazon.com/
- 免费套餐：EC2 t2.micro（12个月免费）

**快速开始：**
1. 注册 AWS 账号
2. 进入 EC2 控制台
3. 启动实例（选择免费套餐）
4. 配置安全组（开放端口 11434）

### 3. 阿里云（国内用户推荐）

**优点：**
- 国内访问速度快
- 中文界面
- 价格相对便宜

**注册：**
- 网站：https://www.aliyun.com/
- 新用户有优惠

**快速开始：**
1. 注册账号
2. 购买 ECS 实例
3. 选择 Ubuntu 系统
4. 配置安全组

### 4. 腾讯云

**优点：**
- 国内服务，速度快
- 新用户有优惠

**注册：**
- 网站：https://cloud.tencent.com/

### 5. Vultr

**优点：**
- 价格便宜（$2.5/月起）
- 全球多个数据中心
- 按小时计费

**注册：**
- 网站：https://www.vultr.com/

### 6. Linode（现为 Akamai）

**优点：**
- 性能稳定
- 价格合理

**注册：**
- 网站：https://www.linode.com/

## 推荐方案（按需求）

### 方案 1: 最便宜（适合测试）

**Vultr - $2.5/月**
- 512MB RAM
- 适合测试 Ollama（可能较慢）

### 方案 2: 性价比最高（推荐）

**DigitalOcean - $6/月**
- 1GB RAM
- 1 vCPU
- 25GB SSD
- 适合运行 Ollama phi3:mini

### 方案 3: 免费试用

**AWS 免费套餐**
- 12个月免费
- t2.micro 实例
- 1GB RAM（可能不够运行 Ollama）

## 快速部署步骤（以 DigitalOcean 为例）

### 步骤 1: 注册并创建服务器

1. 访问：https://www.digitalocean.com/
2. 注册账号（可能需要信用卡）
3. 点击 "Create" → "Droplets"
4. 选择：
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic - $6/月（1GB RAM）
   - **Region**: 选择离你最近的区域
   - **Authentication**: SSH keys 或 Password
5. 点击 "Create Droplet"

### 步骤 2: 连接到服务器

创建完成后，你会获得一个 IP 地址，例如：`123.45.67.89`

**Windows 用户：**
- 使用 PuTTY 或 Windows Terminal
- 或使用 PowerShell：

```powershell
ssh root@your-server-ip
```

**Mac/Linux 用户：**
```bash
ssh root@your-server-ip
```

### 步骤 3: 安装 Ollama

连接到服务器后，运行：

```bash
# 安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull phi3:mini

# 启动服务（确保在后台运行）
nohup ollama serve &
```

### 步骤 4: 配置防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 11434/tcp
sudo ufw enable

# 或使用 iptables
sudo iptables -A INPUT -p tcp --dport 11434 -j ACCEPT
```

### 步骤 5: 测试服务

在浏览器中访问：
```
http://your-server-ip:11434
```

应该能看到 Ollama 的响应。

### 步骤 6: 在 Streamlit Cloud 配置

在 Streamlit Cloud Secrets 中添加：
```toml
[ollama]
api_url = "http://your-server-ip:11434"
```

## 使用 Docker（更简单的方式）

如果你熟悉 Docker，可以更简单地部署：

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 运行 Ollama 容器
docker run -d -p 11434:11434 --name ollama ollama/ollama

# 下载模型
docker exec -it ollama ollama pull phi3:mini
```

## 成本对比

| 服务商 | 最低价格 | RAM | 适合场景 |
|--------|---------|-----|----------|
| Vultr | $2.5/月 | 512MB | 测试（可能不够） |
| DigitalOcean | $6/月 | 1GB | **推荐** |
| AWS 免费套餐 | 免费（12个月） | 1GB | 试用 |
| 阿里云 | ¥24/月 | 1GB | 国内用户 |
| 腾讯云 | ¥50/月 | 1GB | 国内用户 |

## 免费选项

### 1. AWS 免费套餐
- 12个月免费
- t2.micro 实例
- 1GB RAM（可能不够运行 Ollama）

### 2. Google Cloud 免费套餐
- $300 免费额度（90天）
- 可以运行小型实例

### 3. Oracle Cloud 免费套餐
- 永久免费（有限制）
- 2个 VM 实例

## 安全注意事项

### ⚠️ 如果使用 HTTP（不安全）

如果 Ollama 使用 HTTP（非 HTTPS）：
- 数据可能被截获
- 建议：
  1. 使用 VPN 连接
  2. 或配置 HTTPS（需要域名和 SSL 证书）
  3. 或使用 IP 白名单限制访问

### 🔒 配置防火墙

只允许 Streamlit Cloud 的 IP 访问（如果可能）：
```bash
# 只允许特定 IP 访问
sudo ufw allow from streamlit-cloud-ip to any port 11434
```

## 推荐流程

**对于新手：**
1. 注册 DigitalOcean（最简单）
2. 创建 $6/月的 Droplet
3. 安装 Ollama
4. 配置 Streamlit Secrets

**对于有经验的用户：**
1. 使用 AWS 免费套餐（12个月）
2. 或使用 Docker 部署

## 快速链接

- **DigitalOcean**: https://www.digitalocean.com/
- **AWS**: https://aws.amazon.com/
- **Vultr**: https://www.vultr.com/
- **阿里云**: https://www.aliyun.com/
- **腾讯云**: https://cloud.tencent.com/

## 下一步

选择云服务商后：
1. 注册账号
2. 创建服务器实例
3. 按照上面的步骤安装 Ollama
4. 在 Streamlit Cloud 配置 Secrets
5. 完成！

