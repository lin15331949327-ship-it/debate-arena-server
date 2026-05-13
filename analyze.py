#!/usr/bin/env python
"""analyze.py — 扫描 sessions/ 下所有 JSON，输出辩论质量摘要报告"""
import sys, io, json, os, glob
from collections import Counter, defaultdict

# Fix Windows GBK emoji crash
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SESSION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")

def load_sessions():
    sessions = []
    for f in sorted(glob.glob(os.path.join(SESSION_DIR, "*.json")),
                    key=os.path.getmtime, reverse=True):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            # 只处理有碰撞日志的完整辩论会话
            if data.get("collision_log") and data.get("topic"):
                data["_file"] = f
                sessions.append(data)
        except Exception:
            pass
    return sessions

def analyze(sessions):
    if not sessions:
        print("No session data found.")
        return

    total_turns = sum(len(s["history"]) for s in sessions if "history" in s)
    total_collisions = sum(len(s["collision_log"]) for s in sessions)
    avg_collisions = total_collisions / len(sessions) if sessions else 0

    # 每个 Agent 的平均分数
    agent_scores = defaultdict(list)
    for s in sessions:
        quality = s.get("quality", {})
        for score in quality.get("scores", []):
            agent_scores[score.get("agent", "?")].append(score)

    # 碰撞对统计
    pair_counter = Counter()
    type_counter = Counter()
    for s in sessions:
        for c in s.get("collision_log", []):
            fr = c.get("from", "?")
            to = c.get("to", "?")
            pair_counter[f"{fr} → {to}"] += 1
            type_counter[c.get("type", "?")] += 1

    # quality_score 分布
    score_dist = Counter()
    for s in sessions:
        q = s.get("quality", {})
        sc = q.get("quality_score", 0)
        bucket = f"{sc//10*10}-{sc//10*10+9}" if sc < 100 else "100"
        score_dist[bucket] += 1

    # 最佳辩题（按碰撞数）
    topic_rank = sorted(sessions, key=lambda s: len(s.get("collision_log", [])), reverse=True)

    # 辩题与碰撞类型关联
    topic_types = defaultdict(lambda: Counter())
    for s in sessions:
        topic = s.get("topic", "?")
        for c in s.get("collision_log", []):
            topic_types[topic][c.get("type", "?")] += 1

    # ═════════ 输出 ═════════
    print("=" * 65)
    print("  三Agent 辩论场 — 质量分析报告")
    print("=" * 65)
    print(f"\n📊 总览")
    print(f"  总场次:     {len(sessions)}")
    print(f"  总发言数:   {total_turns}")
    print(f"  总碰撞数:   {total_collisions}")
    print(f"  场均碰撞:   {avg_collisions:.1f}")

    print(f"\n🎭 Agent 平均分 (disagreement / depth / creativity / intensity)")
    for agent in ["zhuangzi", "nietzsche", "beauvoir"]:
        scores = agent_scores.get(agent, [])
        if scores:
            avg_d = sum(s.get("disagreement", 0) for s in scores) / len(scores)
            avg_dp = sum(s.get("depth", 0) for s in scores) / len(scores)
            avg_c = sum(s.get("creativity", 0) for s in scores) / len(scores)
            avg_i = sum(s.get("intensity", 0) for s in scores) / len(scores)
            name = {"zhuangzi": "庄周", "nietzsche": "尼采", "beauvoir": "波伏娃"}.get(agent, agent)
            print(f"  {name:6s}: 分歧 {avg_d:.1f}  深度 {avg_dp:.1f}  创造力 {avg_c:.1f}  强度 {avg_i:.1f}  ({len(scores)}轮)")

    print(f"\n⚔️ 碰撞最多的 Agent 对 (top 10)")
    for (pair, count) in pair_counter.most_common(10):
        print(f"  {pair}: {count}次")

    print(f"\n📈 quality_score 分布")
    for bucket in sorted(score_dist.keys(), key=lambda x: int(x.split('-')[0])):
        bar = "█" * score_dist[bucket]
        print(f"  {bucket:>5}: {bar} {score_dist[bucket]}")

    print(f"\n🏆 最佳辩题 top 5（按碰撞数）")
    for i, s in enumerate(topic_rank[:5], 1):
        collisions = len(s.get("collision_log", []))
        q = s.get("quality", {})
        print(f"  {i}. [{collisions}次碰撞] {s['topic']}  (质量:{q.get('verdict','?')} 分:{q.get('quality_score','?')})")

    print(f"\n🔗 辩题与碰撞类型关联")
    for topic in sorted(topic_types.keys()):
        types = topic_types[topic]
        if types.total() >= 3:  # 只显示有足够碰撞的话题
            type_str = " | ".join(f"{t}:{c}" for t, c in types.most_common(3))
            print(f"  {topic}: {type_str}")

    print(f"\n{'=' * 65}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="辩论质量分析")
    parser.add_argument("--recent", type=int, default=0, help="只看最近N场")
    args = parser.parse_args()

    sessions = load_sessions()  # 已按文件时间倒序排列
    if args.recent > 0:
        sessions = sessions[:args.recent]
        print(f"[仅显示最近 {len(sessions)} 场]\n")
    analyze(sessions)
