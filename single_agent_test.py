"""single_agent_test.py v2 - Phase 2: Single agent role consistency (direct API calls)"""
import os, json, time, sys
from pathlib import Path
import requests

sys.path.insert(0, "E:/debate-arena")
from agents.prompts import AGENT_PROMPTS
from search import search

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
AGENT_NAMES = {"zhuangzi":"庄周","nietzsche":"尼采","beauvoir":"波伏娃"}

TEST_QUESTIONS = [
    "自由是什么？","人为什么活着？","什么是真正的幸福？",
    "死亡意味着什么？","人应该追求什么？","平等有可能实现吗？",
    "痛苦有价值吗？","爱是什么？","知识是力量还是枷锁？","社会规范应该被遵守还是被打破？",
]

def call_ds(system, user, max_tokens=400):
    r = requests.post(API_URL,
        headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},
        json={"model":MODEL,"messages":[{"role":"system","content":system},{"role":"user","content":user}],
              "max_tokens":max_tokens,"temperature":0.7},
        timeout=90)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"].strip()
    return f"[ERR {r.status_code}]"

def test_agent(agent, questions):
    prompt = AGENT_PROMPTS[agent]
    results = []
    print(f"\n--- {AGENT_NAMES[agent]} ({agent}) ---")
    
    for i, q in enumerate(questions):
        t0 = time.time()
        kb = search(agent, q, top_k=2)
        kb_text = "\n".join(f"> {t[:150]}" for t in kb) if kb else ""
        context = f"{kb_text}\n\n问题: {q}" if kb_text else q
        
        answer = call_ds(prompt, context)
        elapsed = time.time() - t0
        
        checks = _check_role_consistency(agent, answer)
        score = sum(1 for v in checks.values() if v) / max(len(checks), 1)
        status = "PASS" if score >= 0.6 else "FAIL"
        print(f"  [{i+1:02d}] {status} s={score:.0%} {q[:25]}... ({elapsed:.1f}s)", flush=True)
        results.append({"question":q,"answer":answer[:300],"score":score,"checks":checks})
    
    passed = sum(1 for r in results if r["score"] >= 0.6)
    pct = passed/len(questions) if questions else 0
    print(f"  TOTAL: {passed}/{len(questions)} ({pct:.0%})")
    return results, pct

def _check_role_consistency(agent, text):
    checks = {}
    if agent == "zhuangzi":
        checks["classical_style"] = any(w in text for w in ["者","也","乎","矣","曰","道","逍遥","齐物","自然"])
        checks["parable"] = any(w in text for w in ["鱼","鸟","蝴蝶","树","牛","鲲","鹏","梦","江湖","风","天"])
        checks["not_modern"] = not any(w in text for w in ["资本主义","女性主义","心理学","数据","系统"])
    elif agent == "nietzsche":
        checks["intense"] = any(w in text for w in ["!","超越","克服","创造","深渊","力量","强大","弱者","超人"])
        checks["power_will"] = any(w in text for w in ["权力意志","力量","意志","生命","主人","奴隶"])
        checks["not_passive"] = not any(w in text for w in ["接受","顺其自然","无所谓","随缘"])
    elif agent == "beauvoir":
        checks["analytical"] = any(w in text for w in ["处境","结构","条件","但是","然而","因此","被","他者"])
        checks["gender_aware"] = any(w in text for w in ["女人","压迫","解放","不平等","主体","客体","自由"])
        checks["concrete"] = any(w in text for w in ["具体","实践","行动","条件","处境"])
    return checks

if __name__ == "__main__":
    print("=== Phase 2: Single Agent Role Test ===\n")
    if not API_KEY:
        print("[ERR] DEEPSEEK_API_KEY not set"); exit(1)
    
    overall = {}
    for agent in ["zhuangzi","nietzsche","beauvoir"]:
        results, pct = test_agent(agent, TEST_QUESTIONS)
        overall[agent] = {"passed":pct,"results":results}
    
    avg = sum(o["passed"] for o in overall.values()) / 3
    print(f"\nOverall: {avg:.0%} role consistency")
    print(f"Target: >80%  {'PASS' if avg>=0.8 else 'FAIL'}")
    
    report = {"test":"single_agent_role_test","target":0.8,"actual":round(avg,2),
              "details":{a:{"score":round(o["passed"],2)} for a,o in overall.items()}}
    rp = Path("E:/debate-arena/sessions/single_agent_test.json")
    with open(rp,'w',encoding='utf-8') as f: json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report: {rp}")
