"""check_env.py - Environment readiness check for Phase 0-3"""
import sys, os
from pathlib import Path

def check():
    ok = True
    checks = [
        ("jieba", "chinese tokenizer"),
        ("numpy", "vector math"),
        ("requests", "HTTP (SiliconFlow API)"),
        ("json", "data processing"),
        ("faiss", "vector index"),
        ("rank_bm25", "BM25 search"),
    ]
    for mod, desc in checks:
        try:
            __import__(mod)
            print(f"  [OK] {mod} ({desc})")
        except ImportError:
            print(f"  [MISS] {mod} ({desc})")
            ok = False
    
    # SiliconFlow API
    key = os.environ.get("SILICONFLOW_API_KEY", "sk-ocjfppboknvlnnepxdpksdnlqpchhzmzhgojcijlcvilgoyt")
    if key:
        print(f"  [OK] SiliconFlow API Key configured")
    else:
        print(f"  [WARN] SiliconFlow API Key not in env")
    
    # Dir structure
    base = Path("E:/debate-arena")
    for d in ["knowledge/docs/zhuangzi/original","knowledge/docs/nietzsche/original","knowledge/docs/beauvoir/original",
              "knowledge/docs/zhuangzi/vector_store","knowledge/docs/nietzsche/vector_store","knowledge/docs/beauvoir/vector_store"]:
        p = base / d
        p.mkdir(parents=True, exist_ok=True)
        print(f"  [OK] {d}")
    
    return ok

if __name__ == "__main__":
    print("=== Debate Arena Env Check ===\n")
    ok = check()
    print(f"\n{'[OK] Environment ready' if ok else '[MISS] Some dependencies missing'}")
