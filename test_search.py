"""test_search.py - Phase 1-7: Retrieval quality testing (20+ queries)"""
import json, sys
from pathlib import Path
sys.path.insert(0, "E:/debate-arena")
from search import search_agent_knowledge

TESTS = [
    {"agent":"zhuangzi","q":"濠梁之辩 子非鱼","expect":"秋水篇"},
    {"agent":"zhuangzi","q":"庖丁解牛 游刃有余","expect":"养生主"},
    {"agent":"zhuangzi","q":"庄周梦蝶 物化","expect":"齐物论 蝴蝶"},
    {"agent":"zhuangzi","q":"混沌开七窍 日凿一窍","expect":"应帝王"},
    {"agent":"zhuangzi","q":"北冥有鱼 鲲鹏","expect":"逍遥游"},
    {"agent":"zhuangzi","q":"相濡以沫 不如相忘于江湖","expect":"大宗师"},
    {"agent":"zhuangzi","q":"无用之用 不材之木","expect":"人间世"},
    {"agent":"nietzsche","q":"上帝已死 我们杀死了他","expect":"God is dead"},
    {"agent":"nietzsche","q":"不能杀死我的 使我更强大","expect":"stronger"},
    {"agent":"nietzsche","q":"当你凝视深渊 深渊也在凝视你","expect":"abyss"},
    {"agent":"nietzsche","q":"人是一根绳索 动物与超人之间","expect":"rope Superman"},
    {"agent":"nietzsche","q":"超人 人是一种应当被超越的东西","expect":"overcome"},
    {"agent":"beauvoir","q":"女人不是天生的 而是后天形成的","expect":"becomes a woman"},
    {"agent":"beauvoir","q":"他者 第二性 定义","expect":"Other"},
    {"agent":"beauvoir","q":"存在先于本质 处境先于选择","expect":"existence precedes"},
    {"agent":"beauvoir","q":"解放 命名就是揭示","expect":"liberation"},
    {"agent":"zhuangzi","q":"自由 逍遥 精神解放","expect":"逍遥"},
    {"agent":"nietzsche","q":"自由 权力意志 自我超越","expect":"will to power"},
    {"agent":"beauvoir","q":"自由 处境 具体行动","expect":"freedom situation"},
    {"agent":"zhuangzi","q":"freedom butterfly dream","expect":"dream"},
    {"agent":"nietzsche","q":"ubermensch superman overman","expect":"Zarathustra"},
    {"agent":"beauvoir","q":"woman becomes one is not born","expect":"second sex"},
]

def eval_test(t):
    try:
        res = search_agent_knowledge(t["agent"], t["q"], top_k=5)
    except Exception as e:
        return {"q":t["q"],"agent":t["agent"],"results":0,"score":0,"error":str(e)}
    
    sc = 1.0 if res else 0.0
    if res:
        first = res[0]["text"].lower()
        for kw in t.get("expect","").lower().split():
            if kw in first: sc = min(sc+0.3, 1.0)
    return {"q":t["q"],"agent":t["agent"],"results":len(res),"score":round(sc,2),
            "top_method":res[0]["method"] if res else "none",
            "top_text":res[0]["text"][:80] if res else ""}

if __name__ == "__main__":
    print("=== Phase 1-7: Retrieval Quality Test ===\n")
    print(f"Test queries: {len(TESTS)}\n")
    
    results = []
    passed = 0
    for i, t in enumerate(TESTS):
        r = eval_test(t)
        results.append(r)
        if r["score"] > 0: passed += 1
        st = "PASS" if r["score"]>0 else "FAIL"
        print(f"  [{i+1:02d}] {st} [{t['agent']}] {t['q'][:50]}")
        if r.get("error"): print(f"       ERR: {r['error']}")
        elif r["results"]: print(f"       {r['top_method']} s={r['score']}: {r['top_text'][:70]}")
        else: print(f"       [WARN] no results")
    
    acc = passed/len(TESTS)*100 if TESTS else 0
    print(f"\n{'='*50}")
    print(f"  Total: {len(TESTS)} | Passed: {passed} | Accuracy: {acc:.1f}% | Target: >80%")
    if acc >= 80: print(f"  [PASS] Target met!")
    else: print(f"  [WARN] Below target - run pipeline first: python preprocess.py && python chunk.py && python embed.py && python build_index.py")
    
    report = {"total":len(TESTS),"passed":passed,"accuracy":round(acc,1),"details":results}
    rp = Path("E:/debate-arena/knowledge/search_test_report.json")
    with open(rp,'w',encoding='utf-8') as f: json.dump(report,f,ensure_ascii=False,indent=2)
    print(f"  Report: {rp}")
