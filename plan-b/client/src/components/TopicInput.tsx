/**
 * components/TopicInput.tsx — 话题输入 + 开始按钮
 */

import { useState } from 'react';
import { startDebate } from '../api';
import { useDebateStore } from '../store/debateStore';

const PRESETS = [
  '什么是好的生活？',
  '自由意志存在吗？',
  '痛苦有意义吗？',
  '技术让人类更自由还是更奴役？',
  '爱是自由的选择还是处境的决定？',
  '死亡赋予生命意义还是消解意义？',
];

export default function TopicInput() {
  const [input, setInput] = useState('');
  const [rounds, setRounds] = useState(6);
  const [loading, setLoading] = useState(false);
  const status = useDebateStore((s) => s.status);

  const handleStart = async () => {
    const topic = input.trim();
    if (!topic || loading) return;

    setLoading(true);
    try {
      await startDebate(topic, rounds);
    } catch (err: any) {
      alert(`启动辩论失败: ${err.message}`);
      setLoading(false);
    }
  };

  const isRunning = status === 'running' || status === 'starting';

  return (
    <div className="topic-input">
      <h2 className="topic-input__title">
        🏛️ 三Agent思想辩论场
      </h2>
      <p className="topic-input__subtitle">
        庄子 · 尼采 · 波伏娃 — 跨越时空的思想碰撞
      </p>

      <div className="topic-input__form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleStart()}
          placeholder="输入辩论话题..."
          disabled={isRunning}
          className="topic-input__field"
        />

        <div className="topic-input__controls">
          <label className="topic-input__rounds">
            轮数:
            <select
              value={rounds}
              onChange={(e) => setRounds(Number(e.target.value))}
              disabled={isRunning}
            >
              {[3, 4, 5, 6, 8, 10].map((n) => (
                <option key={n} value={n}>{n} 轮</option>
              ))}
            </select>
          </label>

          <button
            onClick={handleStart}
            disabled={!input.trim() || isRunning || loading}
            className="topic-input__btn"
          >
            {loading ? '⏳ 启动中...' : isRunning ? '🔴 辩论中...' : '⚔️ 开始辩论'}
          </button>
        </div>
      </div>

      <div className="topic-input__presets">
        <span className="topic-input__presets-label">推荐话题:</span>
        {PRESETS.map((p) => (
          <button
            key={p}
            onClick={() => setInput(p)}
            disabled={isRunning}
            className="topic-input__preset"
          >
            {p}
          </button>
        ))}
      </div>
    </div>
  );
}
