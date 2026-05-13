"""debate_feishu.py - Phase 4: Feishu debate integration (direct API, formatted output)"""
import os, time, sys, requests
from pathlib import Path

sys.path.insert(0, "E:/debate-arena")
from agents.prompts import AGENT_PROMPTS
from engine.debate import DebateEngine
from search import enrich_context
from feishu_handler import format_agent_message, AGENT_EMOJI, AGENT_NAMES

API_KEY = os.environ.get("MIMO_API_KEY", "")
API_URL = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"
MODEL = "mimo-v2.5-pro"

def agent_speak(agent, topic, history):
    """Direct API agent call"""
    prompt = AGENT_PROMPTS[agent]
    context = enrich_context(agent, topic, history)
    
    r = requests.post(API_URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": MODEL,
              "messages": [{"role": "system", "content": prompt},
                           {"role": "user", "content": context}],
              "max_tokens": 1500, "temperature": 0.8},
        timeout=90)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"].strip()
    return ""

def run_debate_for_feishu(topic, max_rounds=3):
    """4-3: Async-step debate delivery + 4-2: formatted output"""
    if not API_KEY:
        return "Error: DEEPSEEK_API_KEY not configured"
    
    engine = DebateEngine()
    engine.start(topic=topic, max_rounds=max_rounds)
    
    emoji = AGENT_EMOJI.get(engine.state.speaker_order[0], "")
    name = AGENT_NAMES.get(engine.state.speaker_order[0], "?")
    lines = [f"## {emoji} {topic}\n\n*{name} · {engine.state.speaker_order[1]} · {engine.state.speaker_order[2]} · {max_rounds}�?\n"]
    
    for r in range(1, max_rounds + 1):
        for agent in engine.state.speaker_order:
            speaker = engine.next_speaker()
            if not speaker or engine.state.phase == "ended":
                break
            
            history = engine.get_context(for_agent=speaker)
            content = agent_speak(speaker, topic, history)
            if not content:
                continue
            
            engine.record_turn(speaker, content)
            
            # 4-2: 格式化消息（颜色/标记/角色�?卡片样式�?            formatted = format_agent_message(speaker, content, r)
            lines.append(formatted)
    
    # 碰撞报告 + 质量评估
    cr = engine.collision_report()
    qr = engine.quality_report()
    lines.append(f"\n---\n⚔️ 碰撞: {cr['total']}�?| �?质量: {qr.get('verdict','?')} ({qr.get('quality_score',0)}�?")
    
    return "\n".join(lines)
