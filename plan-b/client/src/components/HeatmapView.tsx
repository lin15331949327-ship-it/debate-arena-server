/**
 * components/HeatmapView.tsx — D3.js 碰撞热力图 (纯 CSS/SVG 实现，无需 D3)
 */

import { useMemo } from 'react';
import { useDebateStore, AGENTS } from '../store/debateStore';

export default function HeatmapView() {
  const heatmap = useDebateStore((s) => s.heatmap);
  const collisions = useDebateStore((s) => s.collisions);

  if (!heatmap && collisions.length === 0) {
    return null;
  }

  // 如果 engine 返回了完整 heatmap 数据
  if (heatmap && heatmap.matrix && heatmap.agents && heatmap.agents.length > 0) {
    const { matrix, agents, agentIds } = heatmap;
    const n = agents.length;
    const maxVal = Math.max(1, ...matrix.flat());

    const getColor = (val: number) => {
      const intensity = val / maxVal;
      if (intensity === 0) return 'rgba(255,255,255,0.05)';
      // 从蓝到红
      const r = Math.round(30 + intensity * 200);
      const g = Math.round(30 + (1 - intensity) * 120);
      const b = Math.round(180 * (1 - intensity) + 30);
      return `rgba(${r},${g},${b},${0.3 + intensity * 0.7})`;
    };

    return (
      <div className="heatmap-view">
        <h3 className="heatmap-view__title">🔥 碰撞热度矩阵</h3>
        <div className="heatmap-view__grid" style={{ gridTemplateColumns: `60px repeat(${n}, 1fr)` }}>
          {/* 表头 */}
          <div className="heatmap-view__cell heatmap-view__cell--header" />
          {agents.map((agent) => (
            <div key={agent} className="heatmap-view__cell heatmap-view__cell--header">
              {agent}
            </div>
          ))}

          {/* 矩阵 */}
          {matrix.map((row, i) => (
            <>
              <div
                key={`label-${i}`}
                className="heatmap-view__cell heatmap-view__cell--label"
                style={{ color: AGENTS[agentIds[i]]?.color || '#aaa' }}
              >
                {agents[i]}
              </div>
              {row.map((val, j) => (
                <div
                  key={`${i}-${j}`}
                  className="heatmap-view__cell heatmap-view__cell--value"
                  style={{ background: getColor(val) }}
                  title={`${agents[i]} → ${agents[j]}: ${val}`}
                >
                  {val > 0 ? val : ''}
                </div>
              ))}
            </>
          ))}
        </div>

        <div className="heatmap-view__legend">
          <span>低碰撞</span>
          <div className="heatmap-view__gradient" />
          <span>高碰撞</span>
        </div>
      </div>
    );
  }

  // Fallback: 基于碰撞事件摘要
  const summary = useMemo(() => {
    const map: Record<string, Record<string, number>> = {};
    for (const c of collisions) {
      if (!map[c.from]) map[c.from] = {};
      if (!map[c.from][c.to]) map[c.from][c.to] = 0;
      map[c.from][c.to] += c.intensity;
    }
    return map;
  }, [collisions]);

  return (
    <div className="heatmap-view">
      <h3 className="heatmap-view__title">🔥 碰撞记录 ({collisions.length})</h3>
      <div className="heatmap-view__list">
        {collisions.slice(-10).reverse().map((c, i) => (
          <div key={i} className="heatmap-view__item">
            <span style={{ color: AGENTS[c.from]?.color || '#aaa' }}>
              {c.fromName}
            </span>
            <span className="heatmap-view__arrow">→</span>
            <span style={{ color: AGENTS[c.to]?.color || '#aaa' }}>
              {c.toName}
            </span>
            <span className="heatmap-view__type">{c.type}</span>
            <span className="heatmap-view__intensity">
              {'🔥'.repeat(c.intensity)}
            </span>
            <span className="heatmap-view__point">{c.point}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
