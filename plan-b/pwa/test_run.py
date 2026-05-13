#!/usr/bin/env python
"""
一键本地测试 — 三Agent辩论场
用法: python test_run.py "自由是什么" 3
"""
import sys, os, io, json, time

# ── 修复 Windows GBK emoji 崩溃 ──
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── 关键：把项目根目录加入 sys.path ──
PROJECT_ROOT = r"E:\debate-arena"
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "plan-b", "server"))

# ── 导入核心 ──
from engine.debate import DebateEngine
from agents.prompts import AGENT_PROMPTS
import requests

# ── 搜索模块（可选 — 优先 Qdrant 云版） ──
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
    except Exception:
        pass

if HAS_SEARCH and not os.environ.get("SILICONFLOW_API_KEY"):
    try:
        from embed import SILICONFLOW_API_KEY as _sk
        os.environ["SILICONFLOW_API_KEY"] = _sk
    except Exception:
        pass

# ═══════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════
API_KEY = "tp-ce42vsljarxkusirgqby5cilp7knjnwiqciq3gjdeon3edvl"
MODEL = "mimo-v2.5-pro"
API_URL = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"

AGENT_NAMES = {"zhuangzi": "庄周", "nietzsche": "尼采", "beauvoir": "波伏娃"}
AGENT_TEMPS = {"zhuangzi": 0.8, "nietzsche": 0.9, "beauvoir": 0.65}

# ═══════════════════════════════════════════════
def llm_call(system_prompt, user_prompt, max_tokens=1500, temperature=0.8):
    try:
        r = requests.post(API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"model": MODEL,
                  "messages": [{"role": "system", "content": system_prompt},
                               {"role": "user", "content": user_prompt}],
                  "max_tokens": max_tokens, "temperature": temperature},
            timeout=120)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        return f"[API error {r.status_code}: {r.text[:100]}]"
    except Exception as e:
        return f"[LLM error: {e}]"

# ═══════════════════════════════════════════════
def run(topic, max_rounds=3):
    engine = DebateEngine()
    engine.start(topic=topic, max_rounds=max_rounds)
    
    print(f"\n{'='*60}")
    print(f"  辩题: {topic}")
    print(f"  轮次: {max_rounds}")
    print(f"  首发: {AGENT_NAMES.get(engine.state.config.first_speaker)}")
    print(f"{'='*60}\n")
    
    turn = 0
    last_round = 0
    
    while True:
        speaker = engine.next_speaker()
        if not speaker or engine.state.phase == "ended":
            break
        
        rnd = engine.state.round
        if rnd != last_round:
            print(f"\n── 第 {rnd} 轮 ──\n")
            last_round = rnd
        
        name = AGENT_NAMES.get(speaker, speaker)
        print(f"  [{name}] 思考中...", end=" ", flush=True)
        
        # 取上下文
        ctx = engine.get_context(for_agent=speaker)
        
        # RAG 检索（可选）
        if HAS_SEARCH:
            try:
                results = rag_search(speaker, topic, top_k=3)
                if results:
                    rag_block = "## 知识库原文\n" + "\n".join(f"> {r}" for r in results)
                    ctx = rag_block + "\n\n" + ctx
            except Exception:
                pass
        
        # 调用 LLM
        prompt = AGENT_PROMPTS.get(speaker, "")
        temp = AGENT_TEMPS.get(speaker, 0.8)
        content = llm_call(prompt, ctx, temperature=temp)
        
        # 记录
        engine.record_turn(speaker, content)
        turn += 1
        
        print(f"✓ ({len(content)}字)")
        print(f"  ┌──────────────────────────────────────────")
        for line in content.split("\n"):
            print(f"  │ {line}")
        print(f"  └──────────────────────────────────────────")
        
        # 轮间小延迟
        if turn >= 2:
            time.sleep(0.5)
    
    # ── 结束报告 ──
    print(f"\n{'='*60}")
    print(f"  辩论结束 | {turn} 次发言")
    
    report = engine.collision_report()
    quality = engine.quality_report()
    print(f"  碰撞: {report.get('total', 0)} 次")
    print(f"  质量: {quality.get('verdict', '?')} (分数: {quality.get('quality_score', 0)})")
    print(f"{'='*60}\n")
    
    # 保存
    save_path = os.path.join(PROJECT_ROOT, "sessions",
        f"test_{time.strftime('%Y%m%d_%H%M%S')}.json")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump({
            "topic": topic,
            "max_rounds": max_rounds,
            "history": [{"round": h.round, "speaker": h.speaker, "text": h.text}
                        for h in engine.state.history],
            "collision_log": [{"round": c.round, "from": c.from_agent, "to": c.to_agent,
                               "type": c.collision_type, "point": c.point}
                              for c in engine.state.collision_log],
            "quality": quality,
        }, f, ensure_ascii=False, indent=2)
    print(f"  📁 存档: {save_path}")


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "什么是真正的自由？"
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    run(topic, rounds)
