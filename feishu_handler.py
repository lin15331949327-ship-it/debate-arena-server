"""feishu_handler.py - Phase 4: Full Feishu command interface (4-1 to 4-3 complete)"""
import sys, json
from pathlib import Path
sys.path.insert(0, "E:/debate-arena")

from engine.debate import DebateEngine

AGENT_COLORS = {
    "zhuangzi": "blue",
    "nietzsche": "red", 
    "beauvoir": "purple",
}
AGENT_EMOJI = {"zhuangzi": "🌀", "nietzsche": "⚡", "beauvoir": "🔍"}
AGENT_NAMES = {"zhuangzi": "庄周", "nietzsche": "尼采", "beauvoir": "波伏娃"}

async def handle_debate_command(message):
    """4-1: 飞书命令接口 - /debate /debate_status /debate_history /debate_rounds"""
    text = message.get("text", "").strip()
    
    # /debate_status - 查看当前进度
    if text.startswith("/debate_status"):
        return debate_status()
    
    # /debate_history - 过往记录
    if text.startswith("/debate_history"):
        return list_history()
    
    # /debate_rounds <N> <topic> - 设置轮次
    if text.startswith("/debate_rounds"):
        parts = text.split(None, 2)
        try:
            rounds = int(parts[1])
            if rounds not in (3, 6, 9):
                return "回合数只能为 3, 6 或 9"
            topic = parts[2] if len(parts) > 2 else ""
        except (IndexError, ValueError):
            return "Usage: /debate_rounds [3|6|9] [topic]"
        
        if not topic:
            return "请提供辩论话题"
        return await start_debate(topic, rounds)
    
    # /debate <topic> - 默认3轮
    topic = text.replace("/debate", "", 1).strip()
    if not topic:
        return help_text()
    
    return await start_debate(topic, 3)


async def start_debate(topic, rounds=3):
    """启动新辩论"""
    from debate_feishu import run_debate_for_feishu
    try:
        result = run_debate_for_feishu(topic, max_rounds=rounds)
        return result
    except Exception as e:
        return f"Debate error: {e}"


def debate_status():
    """4-1: /debate_status - 查看当前进度"""
    sessions_dir = Path("E:/debate-arena/sessions")
    recent = sorted(sessions_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not recent:
        return "暂无辩论记录。试试 /debate [话题]"
    
    latest = json.loads(recent[0].read_text(encoding='utf-8'))
    phase = latest.get("phase", "?")
    rnd = latest.get("round", 0)
    turns = len(latest.get("history", []))
    collisions = len(latest.get("collision_log", []))
    quality = latest.get("quality_report", {}).get("verdict", "?")
    
    phase_cn = {"in_debate": "辩论中", "closing": "收束阶段", "ended": "已结束"}.get(phase, phase)
    
    return f"""**辩论进度**
    🏷️ 话题: {latest['topic'][:50]}
    📊 状态: {phase_cn}
    🔄 当前轮次: {rnd}/{latest.get('max_rounds', '?')}
    💬 发言数: {turns}
    ⚔️ 碰撞数: {collisions}
    ⭐ 质量评级: {quality}"""


def list_history():
    """4-1: /debate_history - 过往辩论记录"""
    engine = DebateEngine()
    debates = engine.list_debates(limit=10)
    if not debates:
        return "暂无辩论记录。试试 /debate [话题]"
    
    lines = ["**📜 过往辩论记录**\n"]
    for d in debates:
        lines.append(f"- {d['topic']}")
        lines.append(f"  {d['rounds']}轮 · {d['turns']}发言 · {d.get('collisions',0)}碰撞 · {d.get('quality','?')}")
    return "\n".join(lines)


def help_text():
    return """**🌀 三Agent思想辩论场**
`/debate [话题]` — 发起3轮辩论
`/debate_rounds [3|6|9] [话题]` — 指定回合数
`/debate_status` — 查看最近辩论进度
`/debate_history` — 过往辩论记录


**角色介绍**
🌀 **庄周** — 道家，齐物逍遥，笑着看穿一切
⚡ **尼采** — 权力意志，成为你自己
🔍 **波伏娃** — 存在主义，"你首先需要一个可以成为自己的处境"
"""


def format_agent_message(agent, content, round_num):
    """4-2: 消息格式化 - 不同颜色/标记/卡片样式"""
    emoji = AGENT_EMOJI.get(agent, "")
    name = AGENT_NAMES.get(agent, agent)
    color = AGENT_COLORS.get(agent, "default")
    
    # 飞书消息卡片样式 (使用飞书支持的元素)
    header = f"{emoji} **{name}** · 第{round_num}轮"
    
    # 对于飞书，使用分割线和颜色标记
    return f"""---
{header}

{content}
"""
