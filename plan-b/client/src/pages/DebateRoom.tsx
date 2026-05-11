/**
 * pages/DebateRoom.tsx — 辩论室主页
 */

import { useSocket } from '../hooks/useSocket';
import { useDebateStore } from '../store/debateStore';
import TopicInput from '../components/TopicInput';
import DebateStream from '../components/DebateStream';
import HeatmapView from '../components/HeatmapView';
import SpectatorPanel from '../components/SpectatorPanel';

export default function DebateRoom() {
  useSocket(); // 建立 WebSocket 连接

  const status = useDebateStore((s) => s.status);
  const topic = useDebateStore((s) => s.topic);
  const endedData = useDebateStore((s) => s.endedData);
  const error = useDebateStore((s) => s.error);
  const messages = useDebateStore((s) => s.messages);

  return (
    <div className="debate-room">
      {/* 顶部栏 */}
      <header className="debate-room__header">
        <h1 className="debate-room__logo">🏛️ 三Agent思想辩论场</h1>
        <div className="debate-room__status">
          {status === 'idle' && <span className="status-badge status--idle">等待开始</span>}
          {status === 'starting' && <span className="status-badge status--running">启动中...</span>}
          {status === 'running' && <span className="status-badge status--running">辩论中 🔴</span>}
          {status === 'completed' && <span className="status-badge status--completed">已完成 ✅</span>}
          {status === 'error' && <span className="status-badge status--error">出错 ❌</span>}
        </div>
      </header>

      {/* 错误提示 */}
      {error && (
        <div className="debate-room__error">
          ❌ {error}
          <button onClick={() => useDebateStore.getState().setError(null)}>✕</button>
        </div>
      )}

      {/* 辩论标题 */}
      {topic && status !== 'idle' && (
        <div className="debate-room__topic">
          <h2>📜 {topic}</h2>
        </div>
      )}

      {/* 主区域 */}
      <div className="debate-room__main">
        {/* 左: 辩论流 */}
        <div className="debate-room__stream">
          {status === 'idle' ? <TopicInput /> : <DebateStream />}

          {/* 辩论结束摘要 */}
          {status === 'completed' && endedData && (
            <div className="debate-room__summary">
              <h3>📊 辩论总结</h3>
              <div className="summary-grid">
                <div className="summary-item">
                  <span className="summary-value">{endedData.turns}</span>
                  <span className="summary-label">总发言</span>
                </div>
                <div className="summary-item">
                  <span className="summary-value">{endedData.rounds}</span>
                  <span className="summary-label">总轮数</span>
                </div>
                <div className="summary-item">
                  <span className="summary-value">{endedData.collisions}</span>
                  <span className="summary-label">碰撞次数</span>
                </div>
                <div className="summary-item">
                  <span className="summary-value" style={{
                    color: endedData.quality === '优秀' ? '#2ECC71' :
                           endedData.quality === '良好' ? '#4A90E2' :
                           endedData.quality === '一般' ? '#F39C12' : '#E74C3C'
                  }}>
                    {endedData.quality}
                  </span>
                  <span className="summary-label">质量评级</span>
                </div>
                <div className="summary-item">
                  <span className="summary-value">{endedData.score}</span>
                  <span className="summary-label">评分</span>
                </div>
                <div className="summary-item">
                  <span className="summary-value">{endedData.avgIntensity.toFixed(1)}</span>
                  <span className="summary-label">平均碰撞强度</span>
                </div>
              </div>

              {/* 碰撞类型分布 */}
              {endedData.collisionTypes && Object.keys(endedData.collisionTypes).length > 0 && (
                <div className="summary-types">
                  {Object.entries(endedData.collisionTypes).map(([type, count]) => (
                    <span key={type} className="summary-type-badge">
                      {type}: {count}
                    </span>
                  ))}
                </div>
              )}

              <button
                onClick={() => {
                  useDebateStore.getState().reset();
                }}
                className="summary-reset-btn"
              >
                🔄 开始新辩论
              </button>
            </div>
          )}
        </div>

        {/* 右: 热力图 + 旁观者 */}
        <div className="debate-room__sidebar">
          {messages.length > 0 && <HeatmapView />}
          {status === 'running' && <SpectatorPanel />}
        </div>
      </div>

      {/* Agent 快速导航 */}
      {messages.length > 0 && (
        <div className="debate-room__agents">
          <div className="agent-nav">
            <span className="agent-nav__dot agent-nav__dot--zhuangzi">🌀 庄周</span>
            <span className="agent-nav__dot agent-nav__dot--nietzsche">⚡ 尼采</span>
            <span className="agent-nav__dot agent-nav__dot--beauvoir">🔍 波伏娃</span>
          </div>
        </div>
      )}
    </div>
  );
}
