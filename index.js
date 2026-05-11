/**
 * 三Agent辩论场 — Node.js Express + Socket.IO 后端
 * Plan B: 完整 Web 应用
 *
 * 端口: 3001
 * WebSocket 消息协议见文档
 */

import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import { PythonShell } from 'python-shell';
import { v4 as uuidv4 } from 'uuid';
import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: { origin: '*', methods: ['GET', 'POST'] },
  maxHttpBufferSize: 1e8,
  pingTimeout: 120000,
  pingInterval: 25000,
});

app.use(cors());
app.use(express.json());

// ─── 活跃辩论状态 ───────────────────────────────────────────
const activeDebates = new Map(); // debateId → { topic, agents, status, clients }

// ─── Python 桥接路径 ────────────────────────────────────────
const BRIDGE_SCRIPT = join(__dirname, 'bridge.py');
const PYTHON_PATH = 'python'; // 或 'python3'

// ─── 辅助函数 ───────────────────────────────────────────────
function makeDebateId(topic) {
  const short = topic.replace(/[^a-zA-Z0-9\u4e00-\u9fff]/g, '_').slice(0, 20);
  return `${short}_${Date.now()}`;
}

function saveDebateSession(debateId, data) {
  const dir = join('E:/debate-arena/sessions');
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, `web_${debateId}.json`), JSON.stringify(data, null, 2), 'utf-8');
}

// ─── WebSocket 连接管理 ──────────────────────────────────────
io.on('connection', (socket) => {
  console.log(`[WS] 客户端连接: ${socket.id}`);

  socket.on('join_debate', (debateId) => {
    socket.join(`debate:${debateId}`);
    console.log(`[WS] ${socket.id} 加入辩论: ${debateId}`);
  });

  socket.on('leave_debate', (debateId) => {
    socket.leave(`debate:${debateId}`);
    console.log(`[WS] ${socket.id} 离开辩论: ${debateId}`);
  });

  socket.on('disconnect', () => {
    console.log(`[WS] 客户端断开: ${socket.id}`);
  });
});

// ─── HTTP API ────────────────────────────────────────────────

/**
 * POST /api/debate/start
 * Body: { topic, maxRounds?, firstSpeaker? }
 * 启动新辩论 — 调用 Python bridge.py
 */
app.post('/api/debate/start', async (req, res) => {
  const { topic, maxRounds = 6, firstSpeaker } = req.body;

  if (!topic || topic.trim().length === 0) {
    return res.status(400).json({ error: '缺少辩论话题' });
  }

  const debateId = makeDebateId(topic);

  // 检查是否已有进行中的辩论
  if (activeDebates.has(debateId) && activeDebates.get(debateId).status === 'running') {
    return res.status(409).json({ error: '该话题辩论已在进行中', debateId });
  }

  const debate = {
    id: debateId,
    topic,
    agents: ['庄周', '尼采', '波伏娃'],
    agentIds: ['zhuangzi', 'nietzsche', 'beauvoir'],
    status: 'starting',
    startedAt: Date.now(),
    turns: [],
    collisions: [],
    clients: new Set(),
  };
  activeDebates.set(debateId, debate);

  // 广播辩论开始
  io.to(`debate:${debateId}`).emit('debate_started', {
    debateId,
    topic,
    agents: debate.agents,
    agentIds: debate.agentIds,
  });
  // 也广播到全局
  io.emit('debate_started', {
    debateId,
    topic,
    agents: debate.agents,
    agentIds: debate.agentIds,
  });

  debate.status = 'running';
  res.json({ debateId, topic, agents: debate.agents });

  // ─── 异步执行 Python 辩论 pipeline ─────────────────────────
  try {
    const options = {
      mode: 'json',
      pythonPath: PYTHON_PATH,
      pythonOptions: ['-u'],
      args: [debateId, topic, String(maxRounds), firstSpeaker || ''],
    };

    const pyshell = new PythonShell(BRIDGE_SCRIPT, options);

    pyshell.on('message', (message) => {
      try {
        // message 来自 Python 的 print(json) → bridge 逐行输出
        const msg = typeof message === 'string' ? JSON.parse(message) : message;

        switch (msg.type) {
          case 'agent_speaking':
            // Agent 开始思考
            io.to(`debate:${debateId}`).emit('agent_speaking', msg);
            debate.turns.push(msg);
            break;

          case 'debate_message':
            // Agent 发言完成 — 仅发送到对应辩论房间
            io.to(`debate:${debateId}`).emit('debate_message', msg.payload);
            break;
            break;

          case 'heatmap_update':
            // 本轮碰撞矩阵
            const hm = {
              type: 'heatmap_update',
              payload: msg.payload,
              timestamp: Date.now(),
              debateId,
            };
            io.to(`debate:${debateId}`).emit('heatmap_update', hm);
            debate.collisions.push(msg.payload);
            break;

          case 'collision_event':
            // 单次碰撞
            io.to(`debate:${debateId}`).emit('collision_event', msg);
            break;

          case 'quality_update':
            // 质量实时更新
            io.to(`debate:${debateId}`).emit('quality_update', msg);
            break;

          case 'debate_ended':
            // 辩论结束
            debate.status = 'completed';
            debate.endedAt = Date.now();
            debate.qualityReport = msg.payload;
            io.to(`debate:${debateId}`).emit('debate_ended', msg.payload);

            // 保存会话
            saveDebateSession(debateId, {
              ...debate,
              clients: undefined,
              timestamp: new Date().toISOString(),
            });
            console.log(`[辩论] ${debateId} 完成 | 质量: ${msg.payload.quality}`);
            break;

          case 'error':
            debate.status = 'error';
            io.to(`debate:${debateId}`).emit('debate_error', msg);
            io.emit('debate_error', { ...msg, debateId });
            break;

          default:
            console.log(`[Python] 未知消息类型: ${msg.type}`);
        }
      } catch (parseErr) {
        console.log(`[Python stdout] ${message}`);
      }
    });

    pyshell.on('stderr', (stderr) => {
      console.error(`[Python stderr] ${stderr}`);
    });

    pyshell.on('close', (code) => {
      console.log(`[Python] bridge.py 退出 code=${code}`);
      if (code !== 0 && debate.status === 'running') {
        debate.status = 'error';
        const errMsg = { type: 'error', message: `Python bridge 异常退出 (code=${code})`, debateId };
        io.to(`debate:${debateId}`).emit('debate_error', errMsg);
        io.emit('debate_error', errMsg);
      }
      // 清理
      setTimeout(() => {
        if (activeDebates.has(debateId)) {
          activeDebates.get(debateId).status = 'completed';
        }
      }, 60000);
    });

    pyshell.end((err) => {
      if (err) {
        console.error(`[Python] bridge.py end error:`, err.message);
        if (debate.status === 'running') {
          debate.status = 'error';
          io.to(`debate:${debateId}`).emit('debate_error', {
            type: 'error',
            message: err.message,
            debateId,
          });
        }
      }
    });
  } catch (err) {
    console.error('[启动辩论失败]', err);
    debate.status = 'error';
    io.to(`debate:${debateId}`).emit('debate_error', {
      type: 'error',
      message: err.message,
      debateId,
    });
  }
});

/**
 * GET /api/debate/:id/status
 * 查询辩论状态
 */
app.get('/api/debate/:id/status', (req, res) => {
  const debate = activeDebates.get(req.params.id);
  if (!debate) {
    // 尝试从文件读取
    try {
      const filePath = join('E:/debate-arena/sessions', `web_${req.params.id}.json`);
      const data = JSON.parse(readFileSync(filePath, 'utf-8'));
      return res.json({ id: req.params.id, status: 'completed', summary: data });
    } catch {
      return res.status(404).json({ error: '辩论未找到' });
    }
  }
  res.json({
    id: debate.id,
    topic: debate.topic,
    status: debate.status,
    turns: debate.turns.length,
    agents: debate.agents,
  });
});

/**
 * POST /api/spectator/question
 * Body: { debateId, question, from? }
 * 旁观者提问（辩论结束后可选）
 */
app.post('/api/spectator/question', (req, res) => {
  const { debateId, question, from } = req.body;
  if (!debateId || !question) {
    return res.status(400).json({ error: '缺少 debateId 或 question' });
  }

  const debate = activeDebates.get(debateId);
  if (!debate) {
    return res.status(404).json({ error: '辩论未找到' });
  }

  // 广播旁观者提问
  const spectatorMsg = {
    type: 'spectator_question',
    debateId,
    question,
    from: from || '匿名旁观者',
    timestamp: Date.now(),
  };
  io.to(`debate:${debateId}`).emit('spectator_question', spectatorMsg);
  io.emit('spectator_question', spectatorMsg);

  res.json({ success: true });
});

/**
 * GET /api/debates
 * 列出最近的辩论
 */
app.get('/api/debates', (_req, res) => {
  const dir = 'E:/debate-arena/sessions';
  if (!existsSync(dir)) return res.json([]);

  try {
    const files = readdirSync(dir)
      .filter(f => f.startsWith('web_') && f.endsWith('.json'))
      .sort()
      .reverse()
      .slice(0, 20);

    const debates = [];
    for (const f of files) {
      try {
        const data = JSON.parse(readFileSync(join(dir, f), 'utf-8'));
        debates.push({
          id: data.id,
          topic: data.topic,
          status: data.status,
          turns: Array.isArray(data.turns) ? data.turns.length : 0,
          quality: data.qualityReport?.quality,
          timestamp: data.timestamp,
        });
      } catch { /* skip corrupt files */ }
    }
    res.json(debates);
  } catch (e) {
    res.json([]);
  }
});

// ─── 健康检查 ────────────────────────────────────────────────
app.get('/api/health', (_req, res) => {
  res.json({
    status: 'ok',
    activeDebates: activeDebates.size,
    uptime: process.uptime(),
  });
});

// ─── 全局错误处理 ────────────────────────────────────────────
app.use((err, _req, res, _next) => {
  console.error('[Express Error]', err);
  res.status(500).json({ error: err.message || '内部服务器错误' });
});

// ─── 启动服务器 ──────────────────────────────────────────────
const PORT = process.env.PORT || 3001;
httpServer.listen(PORT, () => {
  console.log(`\n╔══════════════════════════════════════════╗`);
  console.log(`║  三Agent辩论场 Plan B Web后端 🏛️       ║`);
  console.log(`║  HTTP:      http://localhost:${PORT}       ║`);
  console.log(`║  WebSocket: ws://localhost:${PORT}        ║`);
  console.log(`║  Python:    ${BRIDGE_SCRIPT}  ║`);
  console.log(`╚══════════════════════════════════════════╝\n`);
});
