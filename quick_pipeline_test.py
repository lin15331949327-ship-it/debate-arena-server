import sys
sys.path.insert(0, "E:/debate-arena")
from pipeline import run_pipeline_debate

r = run_pipeline_debate("自由是什么人真的可以自由吗", max_rounds=6)
if r.get("status") == "completed":
    q = r.get("quality_report", {})
    cr = r.get("collision_report", {})
    print(f"\nStatus: OK")
    print(f"Turns: {len(r.get('turns',[]))}")
    print(f"Collisions: {cr.get('total',0)}")
    print(f"Quality: {q.get('verdict','?')} ({q.get('quality_score',0)})")
else:
    print(f"FAIL: {r}")
