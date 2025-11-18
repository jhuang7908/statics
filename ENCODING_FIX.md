# 修复中文乱码问题

## 问题描述

上传到 GitHub 后，中文显示为乱码，终端中中文也是乱码。

## 原因

1. **批处理文件编码**：Windows 批处理文件默认使用 GBK/ANSI 编码
2. **Git 编码设置**：Git 可能没有正确配置 UTF-8
3. **终端编码**：Windows 终端默认使用 GBK 编码

## 解决方案

### 1. 运行编码修复脚本

```bash
fix_encoding.bat
```

这个脚本会：
- 设置 Git 使用 UTF-8 编码
- 配置 Git 自动处理换行符
- 显示当前编码配置

### 2. 重新提交文件（使用 UTF-8 编码）

```bash
# 设置 Git 编码
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8

# 重新添加文件
git add .

# 重新提交
git commit -m "Fix: 修复中文编码问题"

# 推送到 GitHub
git push origin main
```

### 3. 检查文件编码

确保以下文件使用 UTF-8 编码：
- `README.md`
- `app.py`
- `stats_core.py`
- `ollama_client.py`
- 所有 `.md` 文件

### 4. 在编辑器中设置编码

**VS Code / Cursor:**
1. 打开文件
2. 右下角点击编码（如 "GBK"）
3. 选择 "通过编码重新打开" → "UTF-8"
4. 保存文件

**Notepad++:**
1. 编码 → 转为 UTF-8 编码
2. 保存

### 5. 验证修复

1. 访问 GitHub：https://github.com/jhuang7908/statics
2. 查看 `README.md` 文件
3. 中文应该正常显示

## 已创建的文件

- `.gitattributes` - 确保 Git 正确处理文件编码
- `fix_encoding.bat` - 编码修复脚本

## 预防措施

1. **编辑器设置**：将编辑器默认编码设置为 UTF-8
2. **Git 配置**：已添加到 `fix_encoding.bat`
3. **文件编码**：使用 `.gitattributes` 确保文件编码正确

## 快速修复命令

```bash
# 1. 运行编码修复
fix_encoding.bat

# 2. 重新提交
git add .
git commit -m "Fix: 修复中文编码问题"
git push origin main
```

