/**
 * hooks/useSocket.ts — Socket.IO React Hook
 */

import { useEffect, useRef } from 'react';
import { getSocket, disconnectSocket } from '../api';
import { useDebateStore } from '../store/debateStore';
import type { Socket } from 'socket.io-client';

export function useSocket() {
  const socketRef = useRef<Socket | null>(null);
  const store = useDebateStore();

  useEffect(() => {
    const socket = getSocket();
    socketRef.current = socket;

    const onConnect = () => {
      console.log('[WS] 已连接:', socket.id);
    };

    const onDisconnect = (reason: string) => {
      console.log('[WS] 断开:', reason);
    };

    const onDebateStarted = (data: { debateId: string; topic: string; agents: string[] }) => {
      store.setDebateId(data.debateId);
      store.setTopic(data.topic);
      store.setStatus('running');
      // 加入辩论房间
      socket.emit('join_debate', data.debateId);
    };

    const onDebateMessage = (data: {
      agentId: string; name: string; emoji: string;
      content: string; round: number; warning?: string; debateId?: string;
    }) => {
      store.addMessage({
        agentId: data.agentId,
        name: data.name,
        emoji: data.emoji,
        content: data.content,
        round: data.round,
        warning: data.warning,
      });
      store.setSpeakingAgent(null);
    };

    const onAgentSpeaking = (data: {
      agentId: string; name: string; round: number;
    }) => {
      store.setSpeakingAgent(data.agentId);
    };

    const onCollisionEvent = (data: {
      from: string; to: string; fromName: string; toName: string;
      type: string; point: string; intensity: number; round: number;
    }) => {
      store.addCollision(data);
    };

    const onHeatmapUpdate = (data: {
      type: string; payload: { matrix: number[][]; agents: string[]; agentIds: string[] };
    }) => {
      store.setHeatmap(data.payload);
    };

    const onSpectatorQuestion = (data: {
      debateId: string; question: string; from: string; timestamp: number;
    }) => {
      store.addSpectatorQuestion(data);
    };

    const onDebateEnded = (data: {
      topic: string; turns: number; rounds: number; collisions: number;
      collisionTypes: Record<string, number>; avgIntensity: number;
      quality: string; score: number; stagnationEvents: number;
      topicDeviation: number; heatmap: any; collisionTimeline: any[];
      timestamp: number;
    }) => {
      store.setEndedData(data);
      store.setStatus('completed');
      store.setSpeakingAgent(null);
    };

    const onDebateError = (data: { type: string; message: string }) => {
      store.setError(data.message);
      store.setStatus('error');
      store.setSpeakingAgent(null);
    };

    // 绑定事件
    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    socket.on('debate_started', onDebateStarted);
    socket.on('debate_message', onDebateMessage);
    socket.on('agent_speaking', onAgentSpeaking);
    socket.on('collision_event', onCollisionEvent);
    socket.on('heatmap_update', onHeatmapUpdate);
    socket.on('spectator_question', onSpectatorQuestion);
    socket.on('debate_ended', onDebateEnded);
    socket.on('debate_error', onDebateError);

    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      socket.off('debate_started', onDebateStarted);
      socket.off('debate_message', onDebateMessage);
      socket.off('agent_speaking', onAgentSpeaking);
      socket.off('collision_event', onCollisionEvent);
      socket.off('heatmap_update', onHeatmapUpdate);
      socket.off('spectator_question', onSpectatorQuestion);
      socket.off('debate_ended', onDebateEnded);
      socket.off('debate_error', onDebateError);
      disconnectSocket();
    };
  }, []);

  return socketRef;
}
