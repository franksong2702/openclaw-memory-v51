# -*- coding: utf-8 -*-
"""
OpenClaw 记忆系统 V52.1 - 增强版
改进：
1. 扩展同义词映射（新增英文、饮食、地点等类别）
2. 优化关键词提取（保留完整英文单词、中文 2 字词整体提取）
3. 添加内容摘要关键词（提取核心名词）
"""

import sqlite3
import json
import os
import re
from datetime import datetime
from pathlib import Path

# ========== 配置 ==========
# 动态获取插件目录（修复：兼容 memory-v51 和 memory_v51 两种目录名）
_PLUGIN_DIR = Path(__file__).parent
# 优先使用插件目录下的 memory_v51 子目录（向后兼容）
MEMORY_DIR = _PLUGIN_DIR / "memory_v51"
if not MEMORY_DIR.exists():
    # 如果 memory_v51 不存在，使用插件根目录
    MEMORY_DIR = _PLUGIN_DIR
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = MEMORY_DIR / "memory.db"

# ========== 中文分词和关键词提取 ==========
# 常用中文停用词
STOP_WORDS = set([
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
    '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
    '你', '会', '着', '没有', '看', '好', '自己', '这', '那',
    '他', '她', '它', '们', '这个', '那个', '什么', '怎么', '可以',
    '喜欢', '喝', '吃', '住', '叫', '做', '用', '想', '能', '会'
])

# 扩展同义词映射（V52.1 新增）
SYNONYMS = {
    # 颜色类
    '颜色': ['蓝色', '灰色', '红色', '绿色', '紫色', '粉色', '黑色', '白色', '酒红', '棕'],
    
    # 饮食类（V52.1 新增）
    '咖啡': ['咖啡', '美式', '拿铁', '卡布奇诺', '浓缩', '饮品', '饮料'],
    '茶': ['茶', '绿茶', '红茶', '奶茶'],
    '酒': ['酒', '啤酒', '红酒', '白酒'],
    '菜': ['菜', '川菜', '湘菜', '粤菜', '水煮鱼'],
    '香菜': ['香菜', '芫荽'],
    '芹菜': ['芹菜', '西芹'],
    
    # 地点类（V52.1 新增）
    '上海': ['上海', '浦东', '前滩', '上海市', '城市'],
    '北京': ['北京', '北京市'],
    '日本': ['日本', '东京', '国家'],
    '欧洲': ['欧洲', '国家'],
    
    # 运动健康类
    '健身': ['运动', '锻炼', '健身', '跑步', '瑜伽', '训练', '健身房', '三次'],
    '跑步': ['跑步', '晨跑', '运动'],
    
    # 工作类
    '工作': ['工作', '职业', '上班', '公司', '职位'],
    '会议': ['会议', '开会', '会面'],
    '报告': ['报告', '文档', '文件', '提交'],
    
    # 技术类（V52.1 新增）
    'Python': ['Python', '编程', '代码', '脚本', '语言'],
    'SQL': ['SQL', '数据库', '查询', '表格', '数据'],
    'React': ['React', '前端', '框架', 'JavaScript'],
    '编程': ['编程', '代码', '开发', '软件'],
    
    # 家庭类（V52.1 新增）
    '儿子': ['儿子', '孩子', '子女'],
    '女儿': ['女儿', '孩子', '子女'],
    '生日': ['生日', '出生', '诞辰'],
    
    # 其他
    '红色': ['红色', '酒红', '颜色'],
    '旅游': ['旅游', '旅行', '玩']
}

# 反向同义词（用于匹配）
SYNONYM_REVERSE = {}
for key, values in SYNONYMS.items():
    for v in values:
        if v not in SYNONYM_REVERSE:
            SYNONYM_REVERSE[v] = []
        SYNONYM_REVERSE[v].append(key)

def extract_keywords(text):
    """
    中文关键词提取（V52.1 改进版）
    1. 保留完整英文单词（不拆分）
    2. 中文 2-4 字词整体提取
    3. 提取前 5 个实词（权重高）
    4. 添加同义词扩展
    """
    keywords = []
    
    # 1. 提取英文单词（完整保留）
    english_words = re.findall(r'\b[a-zA-Z]+\b', text)
    for word in english_words:
        if word.lower() not in ['the', 'a', 'an', 'is', 'are']:
            keywords.append(word)
            # 添加英文单词的同义词
            if word in SYNONYM_REVERSE:
                keywords.extend(SYNONYM_REVERSE[word])
    
    # 2. 处理中文部分
    chinese_text = re.sub(r'[a-zA-Z]', ' ', text)
    chinese_text = re.sub(r'[^\u4e00-\u9fa5]', ' ', chinese_text)
    
    # 3. 提取 2-4 字中文词语（整体提取，不拆分）
    chars = [c for c in chinese_text if c.strip()]
    
    # 提取 2 字词
    for i in range(len(chars) - 1):
        word = chars[i] + chars[i+1]
        if word not in STOP_WORDS and len(word.strip()) >= 2:
            keywords.append(word)
            # 添加同义词
            if word in SYNONYM_REVERSE:
                keywords.extend(SYNONYM_REVERSE[word])
    
    # 提取 3-4 字词
    for i in range(len(chars) - 2):
        word = chars[i] + chars[i+1] + chars[i+2]
        if word not in STOP_WORDS:
            keywords.append(word)
    
    # 4. 去重（保持顺序）
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)
    
    # 5. 限制数量（优先保留前面的词）
    return unique_keywords[:15]

def expand_query(query):
    """
    查询扩展（V52.1 增强版）
    1. 添加同义词
    2. 添加子词
    3. 处理英文单词
    """
    expanded = [query]
    
    # 1. 如果是英文单词，添加完整形式
    if re.match(r'^[a-zA-Z]+$', query):
        expanded.append(query.lower())
        expanded.append(query.upper())
    
    # 2. 添加同义词
    if query in SYNONYMS:
        expanded.extend(SYNONYMS[query])
    
    # 3. 添加反向同义词
    if query in SYNONYM_REVERSE:
        expanded.extend(SYNONYM_REVERSE[query])
    
    # 4. 添加子词（2 字以上）
    if len(query) > 2:
        expanded.append(query[:2])
        expanded.append(query[-2:])
    
    return list(set(expanded))

# ========== 数据库初始化 ==========
def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            summary TEXT,
            category TEXT DEFAULT 'general',
            priority INTEGER DEFAULT 5,
            keywords TEXT,
            created_at TEXT,
            updated_at TEXT,
            access_count INTEGER DEFAULT 0
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_category ON memories(category)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_priority ON memories(priority)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_keywords ON memories(keywords)')
    conn.commit()
    conn.close()

# ========== 核心功能 ==========
def generate_id(category):
    prefix = {'personal': 'p', 'task': 't', 'knowledge': 'k', 'preference': 'r'}.get(category, 'm')
    timestamp = datetime.now().strftime('%y%m%d')
    
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM memories WHERE id LIKE ?', (f'{prefix}_{timestamp}_%',))
    seq = c.fetchone()[0] + 1
    conn.close()
    
    return f'{prefix}_{timestamp}_{seq:03d}'

def remember(content, category='general', priority=5):
    """记住用户告诉的事情（V52.1 优化版）"""
    # 生成摘要（前 50 字）
    summary = content[:50] + '...' if len(content) > 50 else content
    
    # 使用改进的关键词提取
    keywords = extract_keywords(content)
    
    memory_id = generate_id(category)
    now = datetime.now().isoformat()
    
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('''
        INSERT INTO memories (id, content, summary, category, priority, keywords, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (memory_id, content, summary, category, priority, json.dumps(keywords, ensure_ascii=False), now, now))
    conn.commit()
    conn.close()
    
    return memory_id

def recall(query, limit=5):
    """检索相关记忆（V52.1 优化版）"""
    # 修复：空查询返回空列表
    if not query or not query.strip():
        return []
    
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    # 扩展查询词
    expanded_queries = expand_query(query)
    
    # 构建多条件查询
    conditions = []
    params = []
    
    for q in expanded_queries:
        # 修复：对 LIKE 特殊字符（% _）进行转义，防止 SQL 注入
        escaped_q = q.replace('%', r'\%').replace('_', r'\_')
        conditions.append('content LIKE ? ESCAPE ?')
        params.append(f'%{escaped_q}%')
        params.append('\\')
        conditions.append('keywords LIKE ? ESCAPE ?')
        params.append(f'%{escaped_q}%')
        params.append('\\')
    
    sql = f'''
        SELECT id, summary, category, priority, keywords, access_count
        FROM memories
        WHERE {" OR ".join(conditions)}
        ORDER BY priority DESC, access_count DESC
        LIMIT ?
    '''
    params.append(limit)
    
    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()
    
    # 更新访问次数
    for row in rows:
        _increment_access(row[0])
    
    return [
        {
            'id': row[0],
            'summary': row[1],
            'category': row[2],
            'priority': row[3],
            'keywords': json.loads(row[4]) if row[4] else [],
            'access_count': row[5]
        }
        for row in rows
    ]

def _increment_access(memory_id):
    """增加访问次数"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('UPDATE memories SET access_count = access_count + 1 WHERE id = ?', (memory_id,))
    conn.commit()
    conn.close()

def get_memory(memory_id):
    """获取指定记忆"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('SELECT id, content, summary, category, priority, keywords, created_at, access_count FROM memories WHERE id = ?', (memory_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'content': row[1],
            'summary': row[2],
            'category': row[3],
            'priority': row[4],
            'keywords': json.loads(row[5]) if row[5] else [],
            'created_at': row[6],
            'access_count': row[7]
        }
    return None

def update_memory(memory_id, content=None, category=None, priority=None):
    """更新记忆（V52.1 新增）"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    updates = []
    params = []
    now = datetime.now().isoformat()
    
    if content is not None:
        updates.append('content = ?')
        params.append(content)
        updates.append('summary = ?')
        params.append(content[:50] + '...' if len(content) > 50 else content)
        # 重新提取关键词
        keywords = extract_keywords(content)
        updates.append('keywords = ?')
        params.append(json.dumps(keywords, ensure_ascii=False))
    
    if category is not None:
        updates.append('category = ?')
        params.append(category)
    
    if priority is not None:
        updates.append('priority = ?')
        params.append(priority)
    
    if not updates:
        conn.close()
        return False
    
    updates.append('updated_at = ?')
    params.append(now)
    params.append(memory_id)
    
    sql = f'UPDATE memories SET {", ".join(updates)} WHERE id = ?'
    c.execute(sql, params)
    conn.commit()
    count = c.rowcount
    conn.close()
    return count > 0

# ========== 工具函数 ==========
def list_memories(category=None, limit=20):
    """列出记忆"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    if category:
        c.execute('SELECT id, summary, category, priority, access_count FROM memories WHERE category = ? ORDER BY created_at DESC LIMIT ?', (category, limit))
    else:
        c.execute('SELECT id, summary, category, priority, access_count FROM memories ORDER BY created_at DESC LIMIT ?', (limit,))
    
    rows = c.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0],
            'summary': row[1],
            'category': row[2],
            'priority': row[3],
            'access_count': row[4]
        }
        for row in rows
    ]

def delete_memory(memory_id):
    """删除记忆"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('DELETE FROM memories WHERE id = ?', (memory_id,))
    conn.commit()
    count = c.rowcount
    conn.close()
    return count > 0

def clear_memories():
    """清空所有记忆"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('DELETE FROM memories')
    conn.commit()
    conn.close()

def get_stats():
    """获取统计信息"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    # 总数
    c.execute('SELECT COUNT(*) FROM memories')
    total = c.fetchone()[0]
    
    # 按类别统计
    c.execute('SELECT category, COUNT(*) FROM memories GROUP BY category')
    by_category = dict(c.fetchall())
    
    conn.close()
    
    return {
        'total': total,
        'by_category': by_category
    }

# ========== 初始化数据库 ==========
if __name__ == '__main__':
    init_db()
    print("V52.1 Database initialized")
