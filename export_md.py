#!/usr/bin/env python
"""export_md.py — 辩论 JSON → 可分发 Markdown
用法: python export_md.py sessions/test_20260513_155719.json
输出: sessions/test_20260513_155719.md
"""
import sys, io, json, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

AGENT_STYLES = {
    "zhuangzi":  {"name": "庄周", "style": "*"},                   # 斜体
    "nietzsche": {"name": "尼采", "style": "**"},                  # 粗体
    "beauvoir":  {"name": "波伏娃", "style": ""},                   # 普通
}

COLLISION_TYPE_NAMES = {
    "直接反驳": "直接反驳",
    "视角转换": "视角转换",
    "系统批判": "系统批判",
}


def export_to_md(session_path):
    with open(session_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    topic = data.get("topic", "未命名辩论")
    history = data.get("history", [])
    collision_log = data.get("collision_log", [])
    quality = data.get("quality", {})

    # 按轮次分组
    rounds = {}
    for h in history:
        r = h.get("round", 1)
        rounds.setdefault(r, []).append(h)

    out_path = os.path.splitext(session_path)[0] + ".md"

    lines = []
    lines.append(f"# {topic}")
    lines.append("")
    lines.append(f"> 三Agent思想辩论场 · 庄周 · 尼采 · 波伏娃")
    lines.append(f"> 生成于 {os.path.basename(session_path)}")
    lines.append("")

    # ── 辩论正文 ──
    for rnd in sorted(rounds.keys()):
        lines.append(f"## 第 {rnd} 轮")
        lines.append("")
        for h in rounds[rnd]:
            speaker = h.get("speaker", "?")
            cfg = AGENT_STYLES.get(speaker, {"name": speaker, "style": ""})
            s = cfg["style"]
            name = cfg["name"]
            text = h.get("text", "").strip()

            lines.append(f"**{name}**  ")
            for paragraph in text.split("\n"):
                paragraph = paragraph.strip()
                if paragraph:
                    if s:
                        lines.append(f"{s}{paragraph}{s}  ")
                    else:
                        lines.append(f"{paragraph}  ")
            lines.append("")
        lines.append("---")
        lines.append("")

    # ── 碰撞统计 ──
    lines.append("## 辩论统计")
    lines.append("")
    lines.append(f"| 项目 | 数值 |")
    lines.append(f"|------|------|")
    lines.append(f"| 发言数 | {len(history)} |")
    lines.append(f"| 碰撞次数 | {len(collision_log)} |")
    lines.append(f"| 轮次 | {len(rounds)} |")

    cr = quality.get("collision_report", {})
    lines.append(f"| 平均碰撞强度 | {cr.get('avg_intensity', '?')} |")

    lines.append(f"| 质量评级 | **{quality.get('verdict', '?')}** |")
    lines.append(f"| 质量分数 | {quality.get('quality_score', '?')} |")
    lines.append(f"| 停滞事件 | {quality.get('stagnation_events', 0)} |")
    lines.append(f"| 跑题度 | {quality.get('topic_deviation', 0)} |")
    lines.append("")

    # ── 碰撞明细 ──
    if collision_log:
        lines.append("### 碰撞明细")
        lines.append("")
        lines.append("| 轮次 | 发起方 | 目标 | 类型 | 强度 |")
        lines.append("|------|--------|------|------|------|")
        for c in collision_log:
            fr = AGENT_STYLES.get(c.get("from", "?"), {}).get("name", c.get("from", "?"))
            to = AGENT_STYLES.get(c.get("to", "?"), {}).get("name", c.get("to", "?"))
            ct = c.get("type", "?")
            ci = c.get("intensity", "?")
            crd = c.get("round", "?")
            lines.append(f"| {crd} | {fr} | {to} | {ct} | {ci} |")
        lines.append("")

    lines.append("---")
    lines.append("*由三Agent辩论引擎自动生成*")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python export_md.py <session.json>")
        print("示例: python export_md.py sessions/test_20260513_155719.json")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"文件不存在: {path}")
        sys.exit(1)

    out = export_to_md(path)
    print(f"已导出: {out}")
