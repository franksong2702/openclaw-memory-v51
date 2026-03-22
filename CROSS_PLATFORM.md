# 跨平台安装指南

OpenClaw Memory V51 插件支持 **Windows**、**macOS** 和 **Linux** 系统。

---

## 🖥️ 系统要求

### 所有平台
- **Node.js** >= 18.x (包含 npm)
- **Git** (用于克隆仓库)

### 可选（用于数据库初始化）
- **Python** >= 3.10

---

## 📦 安装步骤

### 1. 克隆仓库

**所有平台:**
```bash
cd <your-openclaw-extensions-directory>
git clone https://github.com/YOUR_USERNAME/openclaw-memory-v51.git memory-v51
cd memory-v51
```

**OpenClaw extensions 目录位置：**
- **Windows:** `C:\Users\<username>\.openclaw\extensions\`
- **macOS:** `~/.openclaw/extensions/`
- **Linux:** `~/.openclaw/extensions/`

---

### 2. 运行安装脚本

#### Windows (PowerShell)

```powershell
.\install.bat
```

如果提示权限问题，以管理员身份运行 PowerShell。

#### macOS / Linux (Bash)

```bash
chmod +x install.sh
./install.sh
```

---

### 3. 手动安装（如果脚本失败）

```bash
# 安装依赖
npm install

# 编译 TypeScript
npm run build

# 初始化数据库（可选）
python3 memory_core_v2.py
```

---

## ⚙️ 配置 OpenClaw

### 编辑配置文件

**找到配置文件：**

- **Windows:** `C:\Users\<username>\.openclaw\openclaw.json`
- **macOS/Linux:** `~/.openclaw/openclaw.json`

**添加插件配置：**

```json
{
  "plugins": {
    "allow": ["memory-v51"],
    "entries": {
      "memory-v51": {
        "enabled": true
      }
    }
  }
}
```

---

### 重启 OpenClaw Gateway

**所有平台:**
```bash
openclaw gateway restart
```

**或者手动重启：**

**Windows:**
```powershell
# 停止
openclaw gateway stop

# 启动
openclaw gateway start
```

**macOS/Linux:**
```bash
# 按 Ctrl+C 停止当前运行的进程
# 然后启动
openclaw gateway start
```

---

## ✅ 验证安装

### 方法 1: 检查插件状态

```bash
openclaw plugin list
```

应该看到 `memory-v51` 在列表中，状态为 `enabled`。

### 方法 2: 测试记忆功能

在 OpenClaw 对话中测试：

```
记住我喜欢喝美式咖啡，不加糖
我之前说过什么关于咖啡的？
```

### 方法 3: 运行评测脚本

```bash
cd <extensions-directory>/memory-v51
python3 benchmark_v52_1.py
```

---

## 🔧 常见问题

### Windows 问题

**Q: install.bat 运行失败？**

A: 尝试手动执行：
```powershell
npm install
npm run build
python memory_core_v2.py
```

**Q: 中文显示乱码？**

A: 确保 PowerShell 使用 UTF-8 编码：
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

---

### macOS 问题

**Q: 权限错误 "Permission denied"？**

A: 给脚本执行权限：
```bash
chmod +x install.sh
./install.sh
```

**Q: npm 命令找不到？**

A: 安装 Node.js：
```bash
brew install node
```

---

### Linux 问题

**Q: Python 3 找不到？**

A: 安装 Python 3：
```bash
# Ubuntu/Debian
sudo apt-get install python3

# CentOS/RHEL
sudo yum install python3

# Arch Linux
sudo pacman -S python3
```

**Q: 数据库初始化失败？**

A: 确保有写入权限：
```bash
chmod 755 ~/.openclaw/extensions/memory-v51
```

---

## 📊 跨平台测试

已在以下平台测试通过：

| 平台 | 版本 | 状态 |
|------|------|------|
| Windows | 10/11 | ✅ 通过 |
| macOS | 12+ (Monterey+) | ✅ 通过 |
| Linux | Ubuntu 20.04+ | ✅ 通过 |
| WSL2 | Ubuntu 22.04 | ✅ 通过 |

---

## 📝 路径说明

插件使用跨平台路径处理：

- **Python:** 使用 `pathlib.Path` 自动处理路径分隔符
- **Node.js:** 使用 `path.join()` 处理路径
- **数据库:** SQLite 自动处理跨平台兼容性

**数据库位置：**
- **Windows:** `C:\Users\<user>\.openclaw\extensions\memory-v51\memory.db`
- **macOS/Linux:** `~/.openclaw/extensions/memory-v51/memory.db`

---

## 🤝 贡献

遇到平台特定问题？请提交 Issue 说明：
- 操作系统及版本
- Node.js 版本
- Python 版本（如果使用）
- 错误信息

---

**最后更新**: 2026-03-22  
**维护者**: Ein & Frank
