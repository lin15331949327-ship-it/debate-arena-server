"""stress_test.py v2 - Phase 5: Multi-topic debate stress test (direct API, 10 topics from E:\\辩题)"""
import os, json, time, sys
from pathlib import Path
import requests

sys.path.insert(0, "E:/debate-arena")
from agents.prompts import AGENT_PROMPTS
from search import enrich_context
from engine.debate import DebateEngine

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
AGENT_NAMES = {"zhuangzi":"庄周","nietzsche":"尼采","beauvoir":"波伏娃"}

# 10 best topics from E:\辩题, picked for maximum 3-agent collision
TOPICS = [
    "不回应算不算暴力——有人用沉默惩罚你，法律能判ta什么都没做吗",
    "一个人死后，他的名声会在最后一个记得他语气的人死后也死去——那梵高到底哪一年死的",
    "秘密会繁殖吗——你告诉一个人别告诉别人，是不是在帮秘密交配",
    "我们把中等危险全杀光了——秋千被拆长跑被取消——是不是在制造一种新的危险",
    "救一幅伦勃朗还是救一个你不认识的人——你救的到底是生命还是救生命时的自我感动",
    "历史虚无主义有两张脸：一张打开笼子说没有唯一真相，一张换了把锁说既然都是编的我就可以骗你",
    "社会性死亡比生物学死亡先来——你活着但没人在乎你是不是活着——那五十年算活着还是死缓",
    "欲望能不能被制造——如果我所有的想要都是被塞给我的，我还有没有我自己",
    "双重思想不是病是常态——我知道我会死但活得像不会死——病的是让所有人只能有一种思想",
    "看待世界该通过体系还是肉身——地图告诉你尼采怎么想，肉身告诉你三岛闻到的汗",
]

def call_ds(system, user, max_tokens=400, temp=0.8):
    r = requests.post(API_URL,
        headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},
        json={"model":MODEL,"messages":[{"role":"system","content":system},{"role":"user","content":user}],
              "max_tokens":max_tokens,"temperature":temp}, timeout=90)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"].strip()
    return f"[ERR {r.status_code}]"

def run_stress_topic(topic, rounds=6):
    engine = DebateEngine()
    engine.start(topic=topic, max_rounds=rounds)
    errors = 0
    stagnation = 0
    
    for r in range(1, rounds+1):
        for agent in engine.state.speaker_order:
            speaker = engine.next_speaker()
            if not speaker or engine.state.phase == "ended": break
            
            history = engine.get_context(for_agent=speaker)
            enriched = enrich_context(speaker, topic, history)
            answer = call_ds(AGENT_PROMPTS[speaker], enriched, max_tokens=400, temp=0.8)
            
            if answer.startswith("[ERR"):
                errors += 1
            
            warning = engine.record_turn(speaker, answer)
            if warning:
                stagnation += 1
    
    collisions = len(engine.state.collision_log)
    turns = len(engine.state.history)
    quality = engine.quality_report()
    return {"topic":topic,"turns":turns,"errors":errors,"stagnation":stagnation,"collisions":collisions,"quality":quality.get("verdict","?")}

if __name__ == "__main__":
    print("=== Phase 5: Multi-Topic Stress Test ===\n")
    print(f"Topics: {len(TOPICS)} x 6 rounds x 3 agents = {len(TOPICS)*18} turns\n")
    
    if not API_KEY:
        print("[ERR] DEEPSEEK_API_KEY not set"); exit(1)
    
    results = []
    passed = 0
    t0 = time.time()
    
    for i, topic in enumerate(TOPICS):
        t1 = time.time()
        print(f"[{i+1}/{len(TOPICS)}] {topic[:50]}...", end=" ", flush=True)
        r = run_stress_topic(topic)
        results.append(r)
        
        ok = r["errors"] == 0 and r["collisions"] > 0
        if ok: passed += 1
        dt = time.time() - t1
        status = "PASS" if ok else "WARN"
        print(f"{status} t={r['turns']}t c={r['collisions']} e={r['errors']} q={r.get('quality','?')} ({dt:.0f}s)")
    
    elapsed = time.time() - t0
    print(f"\nResults: {passed}/{len(TOPICS)} passed ({passed/len(TOPICS):.0%})")
    print(f"Time: {elapsed:.0f}s ({elapsed/len(TOPICS):.0f}s/topic)")
    
    report = {"test":"multi_topic_stress","topics":len(TOPICS),"passed":passed,
              "accuracy":round(passed/len(TOPICS),2),"time":round(elapsed,1),"details":results}
    rp = Path("E:/debate-arena/sessions/stress_test_report.json")
    with open(rp,'w',encoding='utf-8') as f: json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report: {rp}")
