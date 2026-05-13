"""embed.py - Phase 1-3: Vectorization via SiliconFlow API (BAAI/bge-m3, 1024d)"""
import json, time, os
from pathlib import Path
import numpy as np
import requests

DOCS = Path("E:/debate-arena/knowledge/docs")
API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")
API_URL = "https://api.siliconflow.cn/v1/embeddings"
MODEL = "BAAI/bge-m3"
BATCH = 32
DIM = 1024

def embed_batch(texts):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": MODEL, "input": texts, "encoding_format": "float"}
    
    for attempt in range(3):
        try:
            r = requests.post(API_URL, json=payload, headers=headers, timeout=60)
            if r.status_code == 200:
                d = r.json()
                return [it["embedding"] for it in sorted(d["data"], key=lambda x: x["index"])]
            elif r.status_code == 429:
                wait = 2 ** attempt
                print(f"  rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  API error {r.status_code}: {r.text[:100]}")
                if attempt < 2: time.sleep(2)
        except Exception as e:
            print(f"  request error: {e}")
            if attempt < 2: time.sleep(3)
    print(f"  [FAIL] all retries exhausted, using zero vectors")
    return [[0.0]*DIM]*len(texts)

def embed_agent(agent):
    meta_path = DOCS / agent / "chunks_metadata.json"
    if not meta_path.exists():
        print(f"  [SKIP] {agent}: no chunks_metadata.json"); return
    
    with open(meta_path, 'r', encoding='utf-8') as f: chunks = json.load(f)
    if not chunks:
        print(f"  [SKIP] {agent}: 0 chunks"); return
    
    texts = [c["text"] for c in chunks]
    total = len(texts)
    print(f"  {agent}: {total} chunks to embed ({MODEL}, {DIM}d)")
    
    all_embs = []
    for i in range(0, total, BATCH):
        batch = texts[i:i+BATCH]
        bn = i//BATCH + 1
        tbn = (total+BATCH-1)//BATCH
        t0 = time.time()
        embs = embed_batch(batch)
        all_embs.extend(embs)
        prog = min(i+BATCH, total)
        print(f"    [{bn}/{tbn}] {prog}/{total} ({time.time()-t0:.1f}s)")
    
    vec_dir = DOCS / agent / "vector_store"
    vec_dir.mkdir(parents=True, exist_ok=True)
    
    arr = np.array(all_embs, dtype=np.float32)
    np.save(str(vec_dir / "embeddings.npy"), arr)
    
    ti = [{"id":c["chunk_id"],"source":c["source"],"text":c["text"][:200]} for c in chunks]
    with open(str(vec_dir / "texts.json"),'w',encoding='utf-8') as f: json.dump(ti, f, ensure_ascii=False, indent=2)
    
    print(f"  [DONE] {agent}: {arr.shape} saved")

if __name__ == "__main__":
    print(f"=== Phase 1-3: Embedding ({MODEL}) ===\n")
    for agent in ["zhuangzi","nietzsche","beauvoir"]:
        print(f"--- {agent} ---")
        embed_agent(agent)
