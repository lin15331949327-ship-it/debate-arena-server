#!/usr/bin/env python
"""
bridge.py — Python 辩论引擎桥接 (被 Node.js python-shell 调用)

参数: debate_id topic max_rounds [first_speaker]

输出: 逐行 JSON → Node.js 转发至 Socket.IO
  每行一条 JSON 消息，类型:
  - agent_speaking: Agent 开始思考
  - debate_message: Agent 发言内容
  - heatmap_update: 碰撞热度矩阵
  - collision_event: 单次碰撞
  - debate_ended: 辩论结束
  - error: 错误

严格依赖: E:/debate-arena 的 engine/debate.py + agents/prompts.py
"""
import sys, os, json, time, traceback, io

# Force UTF-8 stdout to prevent emoji→GBK crashes on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ═══════════════════════════════════════════════════════════
# 路径设置
# ═══════════════════════════════════════════════════════════
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.debate import DebateEngine
from agents.prompts import AGENT_PROMPTS

# Requests for LLM calls
import requests

# ═══════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
MODEL = "deepseek-chat"  # fast fallback
API_URL = "https://api.deepseek.com/chat/completions"

AGENT_NAMES = {"zhuangzi": "庄周", "nietzsche": "尼采", "beauvoir": "波伏娃"}
AGENT_EMOJIS = {"zhuangzi": "", "nietzsche": "", "beauvoir": ""}
AGENT_ORDER = ["zhuangzi", "nietzsche", "beauvoir"]

# ═══════════════════════════════════════════════════════════
# LLM 调用
# ═══════════════════════════════════════════════════════════
def llm_call(system_prompt, user_prompt, max_tokens=600, temperature=0.8):
    """LLM call via direct requests (skip litellm for reliability)"""
    if not API_KEY:
        return "[DEEPSEEK_API_KEY not set]"
    try:
        import requests as req
        r = req.post(API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat",
                  "messages": [{"role": "system", "content": system_prompt},
                               {"role": "user", "content": user_prompt}],
                  "max_tokens": max_tokens, "temperature": temperature},
            timeout=120)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        return f"[API error {r.status_code}]"
    except Exception as e:
        return f"[LLM error: {str(e)[:80]}]"

# ═══════════════════════════════════════════════════════════
# 知识库检索 (可选增强)
# ═══════════════════════════════════════════════════════════
try:
    from search import enrich_context
    HAS_SEARCH = True
except (ImportError, ModuleNotFoundError):
    HAS_SEARCH = False

def enrich_if_available(agent, topic, history):
    """如果知识库可用则增强上下文"""
    if HAS_SEARCH:
        try:
            return enrich_context(agent, topic, history)
        except Exception:
            pass
    return history

# ═══════════════════════════════════════════════════════════
# 碰撞矩阵计算
# ═══════════════════════════════════════════════════════════
def build_heatmap_matrix(collision_log):
    """从碰撞记录构建 NxN 热度矩阵"""
    agents = AGENT_ORDER
    n = len(agents)
    idx = {a: i for i, a in enumerate(agents)}
    matrix = [[0] * n for _ in range(n)]

    for c in collision_log:
        # Handle both dataclass objects and dicts
        from_i = idx.get(c.from_agent if hasattr(c, 'from_agent') else c.get("from", ""))
        to_i = idx.get(c.to_agent if hasattr(c, 'to_agent') else c.get("to", ""))
        if from_i is not None and to_i is not None:
            intensity = c.intensity if hasattr(c, 'intensity') else c.get("intensity", 1)
            matrix[from_i][to_i] += intensity
            matrix[to_i][from_i] += intensity

    return {
        "matrix": matrix,
        "agents": [AGENT_NAMES[a] for a in agents],
        "agentIds": agents,
    }

# ═══════════════════════════════════════════════════════════
# 输出辅助
# ═══════════════════════════════════════════════════════════
def output(msg):
    """向 stdout 输出一行 JSON (Node.js 通过 python-shell 接收)"""
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()

# ═══════════════════════════════════════════════════════════
# 辩论 Agent 发言
# ═══════════════════════════════════════════════════════════
def agent_speak(agent, topic, history, round_num):
    """
    Agent 发言生成
    - 使用 AGENT_PROMPTS 作为 system prompt
    - 拼接辩论上下文件为 user prompt
    """
    base_prompt = AGENT_PROMPTS.get(agent, "")
    if not base_prompt:
        return f"[{AGENT_NAMES.get(agent, agent)}]: 无可用提示词"

    # 知识库增强
    enriched_history = enrich_if_available(agent, topic, history)

    return llm_call(base_prompt, enriched_history, max_tokens=600, temperature=0.8)

# ═══════════════════════════════════════════════════════════
# 主辩论流程
# ═══════════════════════════════════════════════════════════
def run_debate(debate_id, topic, max_rounds=6, first_speaker=None):
    """执行完整辩论流程"""

    if not API_KEY:
        output({
            "type": "error",
            "message": "DEEPSEEK_API_KEY 环境变量未设置。请设置后重试。",
            "debateId": debate_id,
        })
        return

    try:
        # 初始化引擎
        engine = DebateEngine(save_dir="E:/debate-arena/sessions")
        engine.start(topic=topic, max_rounds=max_rounds, first_speaker=first_speaker)

        output({
            "type": "log",
            "message": f"辩论引擎启动: {topic} | {max_rounds}轮 | 首发: {AGENT_NAMES.get(engine.state.config.first_speaker, '?')}",
        })

        for r in range(1, max_rounds + 1):
            output({
                "type": "log",
                "message": f"--- 第 {r} 轮开始 ---",
            })

            for agent in engine.state.speaker_order:
                if engine.state.phase == "ended":
                    break

                speaker = engine.next_speaker()
                if not speaker:
                    break

                # 通知前端: Agent 开始思考
                output({
                    "type": "agent_speaking",
                    "agentId": speaker,
                    "name": AGENT_NAMES.get(speaker, speaker),
                    "emoji": AGENT_EMOJIS.get(speaker, ""),
                    "round": r,
                })

                # 获取上下文
                context = engine.get_context(for_agent=speaker)

                # 生成发言
                content = agent_speak(speaker, topic, context, r)
                if not content:
                    content = f"[{AGENT_NAMES.get(speaker, speaker)}] 思考中..."
                # Strip markdown formatting (** ** and * *) from output
                import re as _re
                content = _re.sub(r'\*\*(.+?)\*\*', r'\1', content)
                content = _re.sub(r'(?<!\*)\*(?!\*)([^*]+)(?<!\*)\*(?!\*)', r'\1', content)

                # 记录发言 (引擎内部碰撞检测、导演模块等)
                warning = engine.record_turn(speaker, content)

                # 推送发言消息
                output({
                    "type": "debate_message",
                    "payload": {
                        "agentId": speaker,
                        "name": AGENT_NAMES.get(speaker, speaker),
                        "emoji": AGENT_EMOJIS.get(speaker, ""),
                        "content": content,
                        "round": r,
                        "warning": warning if warning else None,
                    },
                    "timestamp": int(time.time() * 1000),
                })

                # 每轮结束后推送碰撞矩阵
                if engine.state.collision_log:
                    heatmap = build_heatmap_matrix(
                        engine.state.collision_log
                    )
                    output({
                        "type": "heatmap_update",
                        "payload": heatmap,
                    })

                    # 最近一次碰撞
                    latest = engine.state.collision_log[-1]
                    output({
                        "type": "collision_event",
                        "payload": {
                            "from": latest.from_agent,
                            "to": latest.to_agent,
                            "fromName": AGENT_NAMES.get(latest.from_agent, latest.from_agent),
                            "toName": AGENT_NAMES.get(latest.to_agent, latest.to_agent),
                            "collisionType": latest.collision_type,
                            "point": latest.point,
                            "intensity": latest.intensity,
                            "round": latest.round,
                        }
                    })

                # 小延迟（减少 API 压力 + 前端动画可读性）
                if r > 1:
                    time.sleep(0.3)

        # ─── 辩论结束 ───────────────────────────────────
        report = engine.collision_report()
        quality = engine.quality_report()

        # 最终碰撞矩阵
        final_heatmap = build_heatmap_matrix(
            [c.__dict__ for c in engine.state.collision_log] if engine.state.collision_log else []
        )

        # 从 collision_log dataclass 构建
        collision_summary = {
            "matrix": [
                {"from": c.from_agent, "to": c.to_agent, "type": c.collision_type,
                 "intensity": c.intensity, "round": c.round}
                for c in engine.state.collision_log
            ]
        }

        ended_payload = {
            "topic": topic,
            "turns": len(engine.state.history),
            "rounds": engine.state.round,
            "collisions": report.get("total", 0),
            "collisionTypes": report.get("by_type", {}),
            "avgIntensity": report.get("avg_intensity", 0),
            "quality": quality.get("verdict", "未知"),
            "score": quality.get("quality_score", 0),
            "stagnationEvents": quality.get("stagnation_events", 0),
            "topicDeviation": quality.get("topic_deviation", 0),
            "heatmap": final_heatmap,
            "collisionTimeline": collision_summary.get("matrix", []),
            "timestamp": int(time.time() * 1000),
        }

        output({
            "type": "debate_ended",
            "payload": ended_payload,
        })

        output({
            "type": "log",
            "message": f"辩论完成: 碰撞{report.get('total',0)}次 | 质量: {quality.get('verdict','?')} ({quality.get('quality_score',0)})",
        })

    except Exception as e:
        output({
            "type": "error",
            "message": f"辩论执行失败: {str(e)}\n{traceback.format_exc()}",
            "debateId": debate_id,
        })

# ═══════════════════════════════════════════════════════════
# 入口: 从命令行参数启动
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    args = sys.argv[1:]
    debate_id = args[0] if len(args) > 0 else "test_debate"
    topic = args[1] if len(args) > 1 else "什么是好的生活？"
    max_rounds = int(args[2]) if len(args) > 2 else 6
    first_speaker = args[3] if len(args) > 3 and args[3] else None

    output({
        "type": "log",
        "message": f"bridge.py 启动 | debateId={debate_id} | topic={topic}",
    })

    run_debate(debate_id, topic, max_rounds, first_speaker)
