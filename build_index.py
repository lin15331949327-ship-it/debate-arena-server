"""build_index.py - Phase 1-4: FAISS index construction"""
import json
from pathlib import Path
import numpy as np
import faiss

DOCS = Path("E:/debate-arena/knowledge/docs")

def build_index(agent):
    vec_dir = DOCS / agent / "vector_store"
    emb_path = vec_dir / "embeddings.npy"
    if not emb_path.exists():
        print(f"  [SKIP] {agent}: no embeddings.npy"); return
    
    embs = np.load(str(emb_path))
    print(f"  {agent}: {embs.shape[0]} vectors x {embs.shape[1]}d")
    
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embs)
    index.add(embs)
    
    faiss.write_index(index, str(vec_dir / "index.faiss"))
    print(f"  [DONE] {agent}: FAISS index ({index.ntotal} vectors)")

if __name__ == "__main__":
    print("=== Phase 1-4: FAISS Index Building ===\n")
    for agent in ["zhuangzi","nietzsche","beauvoir"]:
        print(f"--- {agent} ---")
        build_index(agent)
