# 🏛️ 三Agent辩论场 — Plan B 完整Web应用

庄子 · 尼采 · 波伏娃 — 跨越时空的 AI 思想碰撞

## 项目架构

```
plan-b/
├── server/          # Node.js Express + Socket.IO 后端
│   ├── index.js     # Express 服务器 + WebSocket
│   ├── bridge.py    # Python 辩论引擎桥接
│   └── package.json
├── client/          # React + Vite + TypeScript 前端
│   ├── src/
│   │   ├── api/index.ts          # HTTP + WebSocket API
│   │   ├── store/debateStore.ts  # Zustand 全局状态
│   │   ├── hooks/useSocket.ts    # Socket.IO React Hook
│   │   ├── components/
│   │   │   ├── TopicInput.tsx     # 话题输入
│   │   │   ├── AgentCard.tsx      # Agent发言卡片
│   │   │   ├── DebateStream.tsx   # 辩论流
│   │   │   ├── HeatmapView.tsx    # 碰撞热力图
│   │   │   └── SpectatorPanel.tsx # 旁观者提问
│   │   ├── pages/DebateRoom.tsx   # 辩论室主页
│   │   └── App.tsx
│   ├── vite.config.ts             # Vite配置(含API代理)
│   └── package.json
└── README.md
```

## 快速启动

### 1. 环境要求

- **Node.js** >= 18
- **Python** >= 3.10
- **DEEPSEEK_API_KEY** 环境变量 (辩论 LLM 调用)

```bash
# 设置 API Key (必需)
set DEEPSEEK_API_KEY=sk-your-key-here

# 或永久设置
setx DEEPSEEK_API_KEY sk-your-key-here
```

### 2. 安装依赖

```bash
# 后端
cd server
npm install

# 前端
cd ../client
npm install
```

### 3. 启动

**启动后端 (端口 3001):**

```bash
cd server
npm start
```

**启动前端 (端口 5173):**

```bash
cd client
npm run dev
```

### 4. 访问

打开浏览器访问 **http://localhost:5173**

## 功能说明

### 辩论流
- 实时推送每个 Agent 的发言 (WebSocket)
- 发言以轮次分组，按角色配色区分
- 辩论进行中显示"思考中..."动画

### 碰撞热力图
- 每轮结束后自动更新碰撞强度矩阵
- 可视化庄周↔尼采↔波伏娃之间的思想碰撞强度
- 颜色深浅：蓝(低) → 红(高)

### 旁观者提问
- 辩论进行中，旁观者可提交问题
- 提问通过 WebSocket 广播给所有客户端

### 辩论总结
- 辩论结束后展示：总发言数、碰撞次数、质量评级、评分
- 碰撞类型分布统计
- 支持"开始新辩论"

## WebSocket 消息协议

```json
// 辩论开始
{"type":"debate_started","payload":{"debateId":"...","topic":"...","agents":["庄周","尼采","波伏娃"]}}

// Agent 发言
{"type":"debate_message","payload":{"agentId":"zhuangzi","name":"庄周","content":"...","round":1}}

// 碰撞热力图更新
{"type":"heatmap_update","payload":{"matrix":[[3,5,2],[5,4,3],[2,3,1]],"agents":["庄周","尼采","波伏娃"]}}

// 辩论结束
{"type":"debate_ended","payload":{"quality":"优秀","score":85,"collisions":15,...}}
```

## HTTP API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/debate/start | 启动新辩论 |
| GET | /api/debate/:id/status | 查询辩论状态 |
| POST | /api/spectator/question | 旁观者提问 |
| GET | /api/debates | 列出最近辩论 |
| GET | /api/health | 健康检查 |

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 19 + TypeScript + Vite + Zustand |
| 实时 | Socket.IO (WebSocket) |
| 后端 | Node.js + Express |
| Python桥 | python-shell + litellm |
| 辩论引擎 | E:/debate-arena/engine/debate.py |
| LLM | DeepSeek API (deepseek-chat) |
| 样式 | 纯 CSS (深色主题) |

## 角色配色

| Agent | 颜色 | Emoji |
|-------|------|-------|
| 庄周 | #4A90E2 蓝 | 🌀 |
| 尼采 | #E74C3C 红 | ⚡ |
| 波伏娃 | #2ECC71 绿 | 🔍 |

## 项目依赖

### 核心依赖: E:/debate-arena

本项目的辩论引擎 (`bridge.py`) 直接导入 `E:/debate-arena` 中的:
- `engine/debate.py` — DebateEngine (6轮调度、碰撞检测、导演模块)
- `agents/prompts.py` — AGENT_PROMPTS (三Agent系统提示词)
- `search.py` — 知识库检索 (可选增强)

## 故障排查

### DEEPSEEK_API_KEY 未设置
```bash
set DEEPSEEK_API_KEY=sk-xxx
# 然后重启 server
```

### Python 模块找不到
```bash
pip install litellm requests
```

### 端口冲突
```bash
# 修改 server/index.js 中的 PORT 或使用环境变量
set PORT=3002
```

### WebSocket 连接失败
确保后端 (3001) 先启动，前端通过 Vite proxy 转发到后端。
