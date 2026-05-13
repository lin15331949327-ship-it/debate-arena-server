#!/usr/bin/env python
"""
三Agent辩论场 — 本地测试启动器 v2
用法: python test_run.py "辩题" [轮数]

变更:
- Qdrant RAG 知识检索已接入
- 崩溃保护（发言不丢失）
- 与 bridge.py 共享 LLM/RAG 逻辑
- Windows GBK 编码修复
"""
import sys, os, io, json, time

# ═══════════════════════════════════════════════════════════
# 0. 环境修复
# ═══════════════════════════════════════════════════════════
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = r"E:\debate-arena"
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "plan-b", "server"))

import requests
from engine.debate import DebateEngine
from agents.prompts import AGENT_PROMPTS

# ═══════════════════════════════════════════════════════════
# 1. RAG 知识检索（优先 Qdrant 云版，降级本地 FAISS）
# ═══════════════════════════════════════════════════════════
# ⚠️ 必须在 import search 模块之前设置，否则 EMBED_API_KEY 已固定为 None
if not os.environ.get("SILICONFLOW_API_KEY"):
    os.environ["SILICONFLOW_API_KEY"] = "sk-ocjfppboknvlnnepxdpksdnlqpchhzmzhgojcijlcvilgoyt"

HAS_SEARCH = False
rag_search = None

try:
    import importlib
    spec = importlib.util.spec_from_file_location(
        "search_qdrant",
        os.path.join(PROJECT_ROOT, "plan-b", "server", "search.py")
    )
    search_qdrant = importlib.util.module_from_spec(spec)
    sys.modules["search_qdrant"] = search_qdrant
    spec.loader.exec_module(search_qdrant)
    rag_search = search_qdrant.search
    HAS_SEARCH = True
    print("[RAG] Qdrant 云版知识库已加载")
except Exception:
    try:
        from search import search as rag_search
        HAS_SEARCH = True
        print("[RAG] 本地 FAISS 版知识库已加载")
    except Exception:
        print("[RAG] 未检测到知识库，辩论将不使用原文引用")

if HAS_SEARCH and not os.environ.get("SILICONFLOW_API_KEY"):
    try:
        from embed import SILICONFLOW_API_KEY as _sk
        os.environ["SILICONFLOW_API_KEY"] = _sk
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════
# 2. 配置
# ═══════════════════════════════════════════════════════════
API_KEY = os.environ.get("MIMO_API_KEY", "")
API_URL = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"
MODEL = "mimo-v2.5-pro"

AGENT_NAMES = {"zhuangzi": "庄周", "nietzsche": "尼采", "beauvoir": "波伏娃"}
AGENT_TEMPERATURES = {"zhuangzi": 0.8, "nietzsche": 0.9, "beauvoir": 0.65}

# ═══════════════════════════════════════════════════════════
# 3. LLM 调用
# ═══════════════════════════════════════════════════════════
def llm_call(system_prompt, user_prompt, temperature=0.8):
    try:
        r = requests.post(API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"model": MODEL,
                  "messages": [
                      {"role": "system", "content": system_prompt},
                      {"role": "user", "content": user_prompt}
                  ],
                  "max_tokens": 1500, "temperature": temperature},
            timeout=120)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        return f"[API error {r.status_code}: {r.text[:100]}]"
    except Exception as e:
        return f"[LLM error: {e}]"

# ═══════════════════════════════════════════════════════════
# 4. 辅助
# ═══════════════════════════════════════════════════════════
def get_last_opponent_text(history, current_speaker):
    """取最近一条非当前 speaker 的发言"""
    for entry in reversed(history):
        if entry.speaker != current_speaker:
            return entry.text
    return ""

# ═══════════════════════════════════════════════════════════
# 5. 主流程
# ═══════════════════════════════════════════════════════════
def run(topic, max_rounds=3):
    engine = DebateEngine()
    engine.start(topic=topic, max_rounds=max_rounds)

    save_path = os.path.join(PROJECT_ROOT, "sessions",
        f"test_{time.strftime('%Y%m%d_%H%M%S')}.json")

    print(f"\n{'='*60}")
    print(f"  辩题: {topic}")
    print(f"  轮次: {max_rounds}")
    print(f"  首发: {AGENT_NAMES.get(engine.state.config.first_speaker)}")
    print(f"  RAG:   {'已启用' if HAS_SEARCH else '未启用'}")
    print(f"{'='*60}\n")

    turn_count = 0
    last_round = 0

    try:
        while True:
            speaker = engine.next_speaker()
            if not speaker or engine.state.phase == "ended":
                break

            rnd = engine.state.round
            if rnd != last_round:
                print(f"\n── 第 {rnd} 轮 ──\n")
                last_round = rnd

            name = AGENT_NAMES.get(speaker, speaker)
            temp = AGENT_TEMPERATURES.get(speaker, 0.8)
            print(f"  [{name}] 思考中...", end=" ", flush=True)

            # 构造上下文
            context = engine.get_context(for_agent=speaker)
            last_opponent = get_last_opponent_text(engine.state.history, speaker)

            # RAG 检索注入
            if HAS_SEARCH:
                try:
                    rag_query = topic
                    if last_opponent:
                        rag_query = f"{topic} {last_opponent[:200]}"
                    results = rag_search(speaker, rag_query, top_k=3)
                    if results:
                        rag_block = "## 知识库检索到的相关原文（必须引用）\n" \
                                    + "\n".join(f"> {r}" for r in results)
                        context = rag_block + "\n\n" + context
                except Exception as e:
                    pass  # RAG 失败静默降级

            # 调用 LLM
            system_prompt = AGENT_PROMPTS.get(speaker, "")
            content = llm_call(system_prompt, context, temperature=temp)

            # 记录
            engine.record_turn(speaker, content)
            turn_count += 1

            print(f"✓ ({len(content)}字)")
            print(f"  ┌{'─'*50}")
            for line in content.split("\n"):
                print(f"  │ {line}")
            print(f"  └{'─'*50}")

            if turn_count >= 2:
                time.sleep(0.3)

        # ── 正常结束 ──
        report = engine.collision_report()
        quality = engine.quality_report()

        print(f"\n{'='*60}")
        print(f"  辩论结束 | {turn_count} 次发言")
        print(f"  碰撞: {report.get('total', 0)} 次 "
              f"(强度 {report.get('avg_intensity', 0):.1f})")
        print(f"  质量: {quality.get('verdict', '?')} "
              f"(分数: {quality.get('quality_score', 0)})")

        if quality.get("stagnation_events", 0):
            print(f"  ⚠️ 停滞事件: {quality['stagnation_events']}")
        if quality.get("topic_deviation", 0) > 0.3:
            print(f"  ⚠️ 跑题度: {quality['topic_deviation']:.2f}")

        print(f"{'='*60}\n")

    finally:
        # 无论正常结束还是崩溃，保存已有发言
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump({
                "topic": topic,
                "max_rounds": max_rounds,
                "phase": getattr(engine.state, 'phase', 'crashed'),
                "history": [
                    {"round": h.round, "speaker": h.speaker, "text": h.text}
                    for h in engine.state.history
                ],
                "collision_log": [
                    {"round": c.round, "from": c.from_agent, "to": c.to_agent,
                     "type": c.collision_type, "point": c.point[:120],
                     "intensity": c.intensity}
                    for c in engine.state.collision_log
                ],
                "quality": quality if 'quality' in dir() else {},
            }, f, ensure_ascii=False, indent=2)
        print(f"  📁 存档: {save_path}")


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "什么是真正的自由？"
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    run(topic, rounds)
