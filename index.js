"use strict";
/**
 * Memory V51 Plugin for OpenClaw
 * Simple SQLite-based memory system
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.tools = void 0;
exports.remember = remember;
exports.recall = recall;
exports.getMemory = getMemory;
exports.register = register;
const sqlite3_1 = __importDefault(require("sqlite3"));
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
// ========== 配置 ==========
const MEMORY_DIR = path_1.default.join(process.env.USERPROFILE || '', '.openclaw', 'extensions', 'memory-v51');
const DB_PATH = path_1.default.join(MEMORY_DIR, 'memory.db');
// 确保目录存在
if (!fs_1.default.existsSync(MEMORY_DIR)) {
    fs_1.default.mkdirSync(MEMORY_DIR, { recursive: true });
}
// ========== 数据库初始化 ==========
function initDb() {
    return new Promise((resolve, reject) => {
        const db = new sqlite3_1.default.Database(DB_PATH, (err) => {
            if (err) {
                console.error('[memory-v51] Failed to open database:', err);
                reject(err);
                return;
            }
            db.serialize(() => {
                db.run(`
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
        `);
                db.run('CREATE INDEX IF NOT EXISTS idx_category ON memories(category)');
                db.run('CREATE INDEX IF NOT EXISTS idx_priority ON memories(priority)');
                console.log('[memory-v51] Database initialized:', DB_PATH);
                db.close();
                resolve();
            });
        });
    });
}
// ========== 辅助函数 ==========
function generateId(category) {
    const prefix = {
        'personal': 'p',
        'task': 't',
        'knowledge': 'k',
        'preference': 'r'
    };
    const p = prefix[category] || 'm';
    const timestamp = new Date().toISOString().slice(2, 10).replace(/-/g, '');
    return new Promise((resolve, reject) => {
        const db = new sqlite3_1.default.Database(DB_PATH, sqlite3_1.default.OPEN_READONLY);
        db.get('SELECT COUNT(*) as count FROM memories WHERE id LIKE ?', [`${p}_${timestamp}_%`], (err, row) => {
            db.close();
            if (err)
                reject(err);
            else {
                const seq = (row?.count || 0) + 1;
                resolve(`${p}_${timestamp}_${seq.toString().padStart(3, '0')}`);
            }
        });
    });
}
// ========== 核心功能 ==========
async function remember(content, category = 'general', priority = 5) {
    const summary = content.length > 50 ? content.slice(0, 50) + '...' : content;
    const keywords = content.split(/\s+/).filter(w => w.length > 1).slice(0, 5);
    const memoryId = await generateId(category);
    const now = new Date().toISOString();
    return new Promise((resolve, reject) => {
        const db = new sqlite3_1.default.Database(DB_PATH);
        db.run(`INSERT INTO memories (id, content, summary, category, priority, keywords, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`, [memoryId, content, summary, category, priority, JSON.stringify(keywords), now, now], (err) => {
            db.close();
            if (err)
                reject(err);
            else
                resolve(memoryId);
        });
    });
}
async function recall(query, limit = 5) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3_1.default.Database(DB_PATH, sqlite3_1.default.OPEN_READONLY);
        db.all(`SELECT id, summary, category, priority, keywords, access_count
       FROM memories
       WHERE content LIKE ? OR summary LIKE ? OR keywords LIKE ?
       ORDER BY priority DESC, access_count DESC
       LIMIT ?`, [`%${query}%`, `%${query}%`, `%${query}%`, limit], (err, rows) => {
            db.close();
            if (err)
                reject(err);
            else {
                const memories = rows.map((row) => ({
                    id: row.id,
                    summary: row.summary,
                    category: row.category,
                    priority: row.priority,
                    keywords: JSON.parse(row.keywords || '[]'),
                    access_count: row.access_count
                }));
                // 更新访问计数
                memories.forEach((m) => {
                    const updDb = new sqlite3_1.default.Database(DB_PATH);
                    updDb.run('UPDATE memories SET access_count = access_count + 1, updated_at = ? WHERE id = ?', [new Date().toISOString(), m.id], () => updDb.close());
                });
                resolve(memories);
            }
        });
    });
}
async function getMemory(memoryId) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3_1.default.Database(DB_PATH, sqlite3_1.default.OPEN_READONLY);
        db.get('SELECT * FROM memories WHERE id = ?', [memoryId], (err, row) => {
            db.close();
            if (err)
                reject(err);
            else if (row) {
                resolve({
                    id: row.id,
                    content: row.content,
                    summary: row.summary,
                    category: row.category,
                    priority: row.priority,
                    keywords: JSON.parse(row.keywords || '[]'),
                    created_at: row.created_at,
                    updated_at: row.updated_at,
                    access_count: row.access_count
                });
            }
            else {
                resolve(null);
            }
        });
    });
}
// ========== OpenClaw 工具定义 ==========
// OpenClaw 会扫描 extensions 目录下的 .js 文件并注册 exported 的工具
exports.tools = {
    remember: {
        description: '记住用户告诉的事情',
        parameters: {
            type: 'object',
            properties: {
                content: { type: 'string', description: '要记住的内容' },
                category: { type: 'string', description: '类别 (personal|task|knowledge|preference|general)', default: 'general' },
                priority: { type: 'number', description: '优先级 (1-10)', default: 5 }
            },
            required: ['content']
        },
        execute: async (args) => {
            try {
                const memoryId = await remember(args.content, args.category, args.priority);
                return JSON.stringify({ status: 'success', memory_id: memoryId });
            }
            catch (e) {
                return JSON.stringify({ status: 'error', message: e.message });
            }
        }
    },
    recall: {
        description: '检索相关记忆',
        parameters: {
            type: 'object',
            properties: {
                query: { type: 'string', description: '搜索关键词' },
                limit: { type: 'number', description: '返回数量上限', default: 5 }
            },
            required: ['query']
        },
        execute: async (args) => {
            try {
                const memories = await recall(args.query, args.limit);
                return JSON.stringify({ status: 'success', memories });
            }
            catch (e) {
                return JSON.stringify({ status: 'error', message: e.message });
            }
        }
    },
    get_memory: {
        description: '获取完整记忆内容',
        parameters: {
            type: 'object',
            properties: {
                memory_id: { type: 'string', description: '记忆 ID' }
            },
            required: ['memory_id']
        },
        execute: async (args) => {
            try {
                const memory = await getMemory(args.memory_id);
                if (memory) {
                    return JSON.stringify({ status: 'success', memory });
                }
                else {
                    return JSON.stringify({ status: 'error', message: 'Memory not found' });
                }
            }
            catch (e) {
                return JSON.stringify({ status: 'error', message: e.message });
            }
        }
    }
};
// ========== OpenClaw 插件注册入口 ==========
// OpenClaw 会调用 exported 的 register 或 activate 函数
async function register() {
    await initDb();
    console.log('[memory-v51] Plugin registered successfully!');
    console.log('[memory-v51] Available tools:', Object.keys(exports.tools));
    return { tools: exports.tools };
}
// ========== 初始化 ==========
async function main() {
    await initDb();
    console.log('[memory-v51] Plugin loaded successfully!');
    console.log('[memory-v51] Available tools:', Object.keys(exports.tools));
}
main().catch(console.error);
//# sourceMappingURL=index.js.map