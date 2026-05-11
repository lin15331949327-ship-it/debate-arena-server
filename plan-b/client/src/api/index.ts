/**
 * api/index.ts — HTTP 接口 + WebSocket 连接管理
 */
import { io, Socket } from 'socket.io-client';

const API_BASE = '/api';
const WS_URL = `http://localhost:3001`;

let socketInstance: Socket | null = null;

export async function startDebate(topic: string, maxRounds = 6, firstSpeaker?: string) {
  const res = await fetch(`${API_BASE}/debate/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, maxRounds, firstSpeaker }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: '启动辩论失败' }));
    throw new Error(err.error || '启动辩论失败');
  }
  return res.json();
}

export async function getDebateStatus(debateId: string) {
  const res = await fetch(`${API_BASE}/debate/${debateId}/status`);
  if (!res.ok) throw new Error('获取状态失败');
  return res.json();
}

export async function getDebates() {
  const res = await fetch(`${API_BASE}/debates`);
  return res.json();
}

export async function sendSpectatorQuestion(debateId: string, question: string, from?: string) {
  const res = await fetch(`${API_BASE}/spectator/question`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ debateId, question, from }),
  });
  return res.json();
}

export function getSocket(): Socket {
  if (!socketInstance) {
    socketInstance = io(WS_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10,
    });
  }
  return socketInstance;
}

export function disconnectSocket() {
  if (socketInstance) {
    socketInstance.disconnect();
    socketInstance = null;
  }
}
