"""pipeline_full.py - Phase 0+1 full pipeline runner"""
import subprocess, sys
from pathlib import Path

BASE = Path("E:/debate-arena")
STEPS = [
    ("Env Check", "check_env.py"),
    ("Preprocess", "preprocess.py"),
    ("Chunking", "chunk.py"),
    ("Concepts", "concept_expand.py"),
    ("Embedding", "embed.py"),
    ("FAISS Index", "build_index.py"),
    ("Search Test", "test_search.py"),
]

if __name__ == "__main__":
    print("="*60)
    print("Debate Arena - Phase 0+1 Full Pipeline")
    print("="*60)
    
    failed = []
    for i, (name, script) in enumerate(STEPS):
        print(f"\n[Step {i+1}/{len(STEPS)}] {name}: {script}")
        sp = BASE / script
        if not sp.exists():
            print(f"  [SKIP] script not found")
            failed.append(name); continue
        try:
            r = subprocess.run([sys.executable, str(sp)], cwd=str(BASE), timeout=600)
            if r.returncode != 0:
                print(f"  [WARN] exit code {r.returncode}")
                failed.append(name)
        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT]")
            failed.append(name)
        except Exception as e:
            print(f"  [ERR] {e}")
            failed.append(name)
    
    print(f"\n{'='*60}")
    if failed: print(f"[WARN] {len(failed)} steps failed: {', '.join(failed)}")
    else: print(f"[DONE] All {len(STEPS)} steps completed!")
    print(f"{'='*60}")
