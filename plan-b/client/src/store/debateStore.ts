/**
 * store/debateStore.ts — Zustand 全局状态管理
 */

import { create } from 'zustand';

// Agent 元数据
export const AGENTS: Record<string, { name: string; emoji: string; color: string }> = {
  zhuangzi: { name: '庄周', emoji: '🌀', color: '#4A90E2' },
  nietzsche: { name: '尼采', emoji: '⚡', color: '#E74C3C' },
  beauvoir: { name: '波伏娃', emoji: '🔍', color: '#2ECC71' },
};

// Agent 发言条目
export interface DebateMessage {
  agentId: string;
  name: string;
  emoji: string;
  content: string;
  round: number;
  warning?: string | null;
}

// 碰撞事件
export interface CollisionEvent {
  from: string;
  to: string;
  fromName: string;
  toName: string;
  type: string;
  point: string;
  intensity: number;
  round: number;
}

// 碰撞矩阵
export interface HeatmapData {
  matrix: number[][];
  agents: string[];
  agentIds: string[];
}

// 旁观者提问
export interface SpectatorQuestion {
  debateId: string;
  question: string;
  from: string;
  timestamp: number;
}

// 辩论结束数据
export interface DebateEndedData {
  topic: string;
  turns: number;
  rounds: number;
  collisions: number;
  collisionTypes: Record<string, number>;
  avgIntensity: number;
  quality: string;
  score: number;
  stagnationEvents: number;
  topicDeviation: number;
  heatmap: HeatmapData;
  collisionTimeline: Array<{
    from: string;
    to: string;
    type: string;
    intensity: number;
    round: number;
  }>;
  timestamp: number;
}

// 全局状态类型
export interface DebateStore {
  // 辩论状态
  debateId: string | null;
  topic: string;
  status: 'idle' | 'starting' | 'running' | 'completed' | 'error';

  // 消息流
  messages: DebateMessage[];
  collisions: CollisionEvent[];
  heatmap: HeatmapData | null;
  spectatorQuestions: SpectatorQuestion[];

  // 结束数据
  endedData: DebateEndedData | null;

  // 错误
  error: string | null;

  // 当前发言者
  speakingAgent: string | null;

  // Actions
  setDebateId: (id: string) => void;
  setTopic: (topic: string) => void;
  setStatus: (status: DebateStore['status']) => void;
  addMessage: (msg: DebateMessage) => void;
  addCollision: (col: CollisionEvent) => void;
  setHeatmap: (hm: HeatmapData) => void;
  addSpectatorQuestion: (q: SpectatorQuestion) => void;
  setEndedData: (data: DebateEndedData) => void;
  setError: (err: string) => void;
  setSpeakingAgent: (agent: string | null) => void;
  reset: () => void;
}

const initialState = {
  debateId: null,
  topic: '',
  status: 'idle' as const,
  messages: [],
  collisions: [],
  heatmap: null,
  spectatorQuestions: [],
  endedData: null,
  error: null,
  speakingAgent: null,
};

export const useDebateStore = create<DebateStore>((set) => ({
  ...initialState,

  setDebateId: (id) => set({ debateId: id }),
  setTopic: (topic) => set({ topic }),
  setStatus: (status) => set({ status }),
  addMessage: (msg) =>
    set((state) => ({ messages: [...state.messages, msg] })),
  addCollision: (col) =>
    set((state) => ({ collisions: [...state.collisions, col] })),
  setHeatmap: (hm) => set({ heatmap: hm }),
  addSpectatorQuestion: (q) =>
    set((state) => ({ spectatorQuestions: [...state.spectatorQuestions, q] })),
  setEndedData: (data) => set({ endedData: data }),
  setError: (err) => set({ error: err }),
  setSpeakingAgent: (agent) => set({ speakingAgent: agent }),
  reset: () => set(initialState),
}));
