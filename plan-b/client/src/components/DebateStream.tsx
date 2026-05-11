/**
 * components/DebateStream.tsx — 辩论流主组件（轮次卡片列表）
 */

import { useEffect, useRef } from 'react';
import { useDebateStore } from '../store/debateStore';
import AgentCard from './AgentCard';

export default function DebateStream() {
  const messages = useDebateStore((s) => s.messages);
  const status = useDebateStore((s) => s.status);
  const speakingAgent = useDebateStore((s) => s.speakingAgent);
  const bottomRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0 && status !== 'running') {
    return (
      <div className="debate-stream debate-stream--empty">
        <p>💭 等待辩论开始...</p>
      </div>
    );
  }

  // 按轮次分组
  const rounds: Record<number, typeof messages> = {};
  for (const msg of messages) {
    if (!rounds[msg.round]) rounds[msg.round] = [];
    rounds[msg.round].push(msg);
  }

  return (
    <div className="debate-stream">
      {Object.entries(rounds).map(([roundNum, msgs]) => (
        <div key={roundNum} className="debate-stream__round">
          <div className="debate-stream__round-header">
            <span>第 {roundNum} 轮</span>
            <span className="debate-stream__round-count">
              {msgs.length}/3 位已发言
            </span>
          </div>
          <div className="debate-stream__cards">
            {msgs.map((msg, i) => (
              <AgentCard
                key={`${msg.agentId}-${msg.round}-${i}`}
                message={msg}
                isNew={i === msgs.length - 1 && msg.round === Number(roundNum)}
              />
            ))}
          </div>
        </div>
      ))}

      {/* 思考中指示器 */}
      {speakingAgent && (
        <div className="debate-stream__thinking">
          <div className="thinking-dots">
            <span className="thinking-dot">●</span>
            <span className="thinking-dot">●</span>
            <span className="thinking-dot">●</span>
            <span className="thinking-text">
              {(() => {
                const map: Record<string, string> = {
                  zhuangzi: '庄周', nietzsche: '尼采', beauvoir: '波伏娃',
                };
                return map[speakingAgent] || speakingAgent;
              })()} 正在思考...
            </span>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
