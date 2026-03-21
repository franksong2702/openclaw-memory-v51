# OpenClaw Memory V52.1 Plugin

🧠 为 OpenClaw 设计的高效记忆系统插件，支持中文语义检索、同义词扩展和优先级管理。

## ✨ 特性

- **中文优化**：n-gram 关键词提取 + 同义词扩展映射
- **语义检索**：支持模糊查询和同义词匹配
- **优先级管理**：1-10 级优先级，重要信息优先检索
- **分类存储**：personal / task / knowledge / preference / general
- **高性能**：平均延迟 <4ms，召回率 100%
- **轻量级**：仅依赖 sqlite3，无需复杂依赖

## 📊 性能指标

| 指标 | V52.1 |
|------|-------|
| **召回率** | 100% (12/12 查询) |
| **F1 分数** | 1.000 |
| **平均延迟** | 3.44ms |
| **综合得分** | 100/100 |

*基于 10 轮跨模型评测（10 个不同 LLM 模型）*

## 🚀 快速安装

### 方法 1: 自动安装脚本（推荐）

```bash
# Windows PowerShell
cd C:\Users\user\.openclaw\extensions
git clone https://github.com/YOUR_USERNAME/openclaw-memory-v51.git memory-v51
cd memory-v51
npm install
npm run build
```

### 方法 2: 手动安装

1. 下载本仓库到 `C:\Users\user\.openclaw\extensions\memory-v51`
2. 安装依赖：`npm install`
3. 编译 TypeScript: `npm run build`
4. 在 OpenClaw 配置中启用插件

### 方法 3: 使用安装脚本

```bash
# Windows
cd C:\Users\user\.openclaw\extensions
powershell -ExecutionPolicy Bypass -File install.bat
```

## 📝 配置

### 启用插件

编辑 `C:\Users\user\.openclaw\openclaw.json`：

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

### 重启 OpenClaw Gateway

```bash
openclaw gateway restart
```

## 🛠️ 使用方法

### API 调用

#### 1. 记住信息 (remember)

```python
from memory_core_v2 import remember

# 简单用法
memory_id = remember("我喜欢喝美式咖啡，不加糖")

# 指定类别和优先级
memory_id = remember(
    "我住在上海前滩东方惠雅小区",
    category="personal",
    priority=9
)
```

#### 2. 检索信息 (recall)

```python
from memory_core_v2 import recall

# 基本检索
results = recall("咖啡")

# 限制返回数量
results = recall("健身", limit=5)
```

#### 3. 获取单条记忆 (get_memory)

```python
from memory_core_v2 import get_memory

memory = get_memory("r_260322_001")
```

### 通过 OpenClaw 工具调用

在 OpenClaw 对话中直接说：

```
记住我喜欢喝美式咖啡，不加糖
我之前说过什么关于健身的？
我的住址是什么？
```

插件会自动检测并调用相应的记忆功能。

## 📁 记忆类别

| 类别 | 说明 | 示例 |
|------|------|------|
| **personal** | 个人信息 | 姓名、住址、家人 |
| **preference** | 偏好习惯 | 饮食喜好、日常习惯 |
| **knowledge** | 知识技能 | 编程语言、工作经验 |
| **task** | 任务计划 | 待办事项、计划安排 |
| **general** | 其他信息 | 不属于以上类别的内容 |

## 🎯 同义词映射

内置同义词扩展，支持自然查询：

```python
SYNONYMS = {
    # 饮食类
    '咖啡': ['美式', '拿铁', '卡布奇诺', '咖啡'],
    '茶': ['绿茶', '红茶', '奶茶', '茶'],
    
    # 地点类
    '上海': ['浦东', '城市', '上海'],
    '北京': ['首都', '北京'],
    
    # 技术类
    'Python': ['编程', '代码', 'Python'],
    'SQL': ['数据库', 'SQL'],
    
    # 运动类
    '健身': ['运动', '锻炼', '健身', '训练'],
    '跑步': ['晨跑', '运动', '跑步'],
    
    # ... 更多类别
}
```

## 🔧 开发

### 环境要求

- Node.js >= 18.x
- Python >= 3.10
- npm >= 9.x

### 构建插件

```bash
# 安装依赖
npm install

# 编译 TypeScript
npm run build

# 运行测试
python benchmark_v52_1.py
```

### 目录结构

```
openclaw-memory-v51/
├── index.ts                 # TypeScript 插件入口
├── index.js                 # 编译后的 JavaScript
├── memory_core_v2.py        # Python 核心模块
├── openclaw.plugin.json     # 插件清单
├── package.json             # Node.js 依赖
├── tsconfig.json            # TypeScript 配置
├── install.bat              # Windows 安装脚本
├── README.md                # 本文档
└── benchmark_v52_1.py       # 性能评测脚本
```

## 📊 评测报告

运行评测脚本生成详细报告：

```bash
cd C:\Users\user\.openclaw\extensions\memory-v51
python benchmark_v52_1.py
```

评测包括：
- 10 轮跨模型测试
- 召回率、精确率、F1 分数
- 延迟性能分析
- 失败查询诊断

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 待办事项

- [ ] 添加模糊匹配（拼写错误容忍）
- [ ] 支持拼音首字母查询
- [ ] 记忆过期机制
- [ ] 向量语义搜索（可选）
- [ ] 更多同义词类别

## 📄 许可证

MIT License

## 🙏 致谢

- OpenClaw 团队提供的插件框架
- lossless-claw 插件的启发
- 所有贡献者和测试用户

## 📞 支持

遇到问题？请提交 Issue 或联系作者。

---

**版本**: V52.1  
**最后更新**: 2026-03-22  
**维护者**: Ein (with help from Frank)
