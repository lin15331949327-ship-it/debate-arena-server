"""phase1_full.py - Phase 1 knowledge base build pipeline"""
import subprocess, sys
from pathlib import Path

BASE = Path("E:/debate-arena")
STEPS = [
    ("env", "check_env.py"),
    ("preprocess", "preprocess.py"),
    ("chunk", "chunk.py"),
    ("concept", "concept_expand.py"),
    ("embed", "embed.py"),
    ("index", "build_index.py"),
    ("test", "test_search.py"),
]

def run_all():
    failed = []
    for name, script in STEPS:
        sp = BASE / script
        print(f"\n[{name}] {script}")
        if not sp.exists():
            print(f"  [SKIP] not found")
            failed.append(name); continue
        try:
            r = subprocess.run([sys.executable, str(sp)], cwd=str(BASE), timeout=600)
            if r.returncode != 0:
                print(f"  [WARN] exit {r.returncode}")
                failed.append(name)
        except Exception as e:
            print(f"  [ERR] {e}")
            failed.append(name)
    
    print(f"\n{'='*40}")
    if failed: print(f"[WARN] Failed: {', '.join(failed)}")
    else: print("[DONE] All steps passed")
    return len(failed) == 0

if __name__ == "__main__":
    run_all()
