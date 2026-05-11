/**
 * components/AgentCard.tsx — 单个Agent发言卡片
 */

import { useMemo } from 'react';
import { AGENTS, type DebateMessage } from '../store/debateStore';

interface Props {
  message: DebateMessage;
  isNew?: boolean;
}

export default function AgentCard({ message, isNew }: Props) {
  const agent = AGENTS[message.agentId];
  if (!agent) return null;

  const isWarning = !!message.warning;

  return (
    <div
      className={`agent-card ${isNew ? 'agent-card--new' : ''} ${isWarning ? 'agent-card--warning' : ''}`}
      style={{ borderLeftColor: agent.color }}
    >
      <div className="agent-card__header">
        <div className="agent-card__avatar" style={{ background: agent.color }}>
          <span className="agent-card__emoji">{message.emoji || agent.emoji}</span>
        </div>
        <div className="agent-card__meta">
          <span className="agent-card__name" style={{ color: agent.color }}>
            {message.name}
          </span>
          <span className="agent-card__round">第 {message.round} 轮</span>
        </div>
        {isNew && <span className="agent-card__badge">NEW</span>}
      </div>

      <div className="agent-card__content">
        {message.content}
      </div>

      {message.warning && (
        <div className="agent-card__warning">
          ⚠️ {message.warning}
        </div>
      )}
    </div>
  );
}
