"""search.py - Phase 1-5: Hybrid BM25 + FAISS retrieval"""
import json, re
from pathlib import Path
import numpy as np
import faiss
import jieba
import requests

DOCS = Path("E:/debate-arena/knowledge/docs")
API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")

_faiss_idx = {}
_texts = {}
_bm25 = {}

def _load(agent):
    if agent in _faiss_idx: return
    vec_dir = DOCS / agent / "vector_store"
    
    # texts
    tp = vec_dir / "texts.json"
    if tp.exists():
        with open(tp,'r',encoding='utf-8') as f: _texts[agent] = json.load(f)
    else:
        mp = DOCS / agent / "chunks_metadata.json"
        if mp.exists():
            with open(mp,'r',encoding='utf-8') as f:
                _texts[agent] = [{"id":c["chunk_id"],"source":c["source"],"text":c["text"]} for c in json.load(f)]
        else:
            _texts[agent] = []
    
    # FAISS
    ip = vec_dir / "index.faiss"
    if ip.exists():
        _faiss_idx[agent] = faiss.read_index(str(ip))
    else:
        _faiss_idx[agent] = None
    
    # BM25
    try:
        from rank_bm25 import BM25Okapi
        corpus = []
        for t in _texts[agent]:
            tokens = [tok.lower().strip() for tok in jieba.cut(t.get("text","")) if tok.strip()]
            corpus.append(tokens)
        _bm25[agent] = BM25Okapi(corpus) if corpus else None
    except: _bm25[agent] = None

def _bm25_search(agent, query, top_k):
    bm = _bm25.get(agent)
    if not bm: return []
    tokens = [tok.lower().strip() for tok in jieba.cut(query) if tok.strip()]
    scores = bm.get_scores(tokens)
    top = scores.argsort()[-top_k:][::-1]
    return [{"idx":int(i),"score":float(scores[i]),"method":"BM25"} for i in top if scores[i]>0]

def _faiss_search(agent, query, top_k):
    idx = _faiss_idx.get(agent)
    if not idx: return []
    try:
        r = requests.post("https://api.siliconflow.cn/v1/embeddings",
            json={"model":"BAAI/bge-m3","input":[query],"encoding_format":"float"},
            headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"}, timeout=30)
        if r.status_code != 200: return []
        qv = np.array(r.json()["data"][0]["embedding"], dtype=np.float32).reshape(1,-1)
        faiss.normalize_L2(qv)
        D, I = idx.search(qv, top_k*2)
        return [{"idx":int(I[0][j]),"score":float(D[0][j]),"method":"FAISS"} for j in range(len(I[0])) if I[0][j]>=0]
    except: return []

def _rrf(bm25_r, faiss_r, top_k, k=60):
    scores = {}
    for rank, it in enumerate(bm25_r):
        scores[it["idx"]] = scores.get(it["idx"],0) + 1.0/(k+rank+1)
    for rank, it in enumerate(faiss_r):
        scores[it["idx"]] = scores.get(it["idx"],0) + 1.0/(k+rank+1)
    return sorted(scores.items(), key=lambda x:x[1], reverse=True)[:top_k]

def search_agent_knowledge(agent, query, top_k=5):
    _load(agent)
    texts = _texts.get(agent, [])
    if not texts: return []
    
    bm = _bm25_search(agent, query, top_k)
    fa = _faiss_search(agent, query, top_k)
    
    if bm and fa:
        fused = _rrf(bm, fa, top_k)
        merged = [{"idx":i,"score":s,"method":"BM25+FAISS"} for i,s in fused]
    elif bm: merged = bm[:top_k]
    elif fa: merged = fa[:top_k]
    else:
        ql = query.lower()
        scored = []
        for i,t in enumerate(texts):
            tx = t.get("text","")
            sc = sum(1 for w in ql.split() if w in tx.lower()) + sum(1 for c in query if c in tx)
            if sc>0: scored.append({"idx":i,"score":float(sc),"method":"keyword"})
        scored.sort(key=lambda x:x["score"], reverse=True)
        merged = scored[:top_k]
    
    res = []
    for it in merged:
        i = it["idx"]
        if i < len(texts):
            t = texts[i]
            res.append({"chunk_id":t.get("id",""),"text":t.get("text",""),"source":t.get("source",""),
                        "score":round(it["score"],4),"method":it["method"]})
    return res

def search(agent, query, top_k=5):
    return [r["text"] for r in search_agent_knowledge(agent, query, top_k)]

def enrich_context(agent, topic, base):
    relevant = search(agent, topic+" "+base, top_k=3)
    if not relevant: return base
    return "## Relevant sources\n" + "\n".join(f"> {r}" for r in relevant) + "\n\n" + base

if __name__ == "__main__":
    for agent in ["zhuangzi","nietzsche","beauvoir"]:
        print(f"--- {agent} ---")
        res = search_agent_knowledge(agent, "自由", top_k=3)
        for i,r in enumerate(res):
            print(f"  [{i+1}] {r['method']} s={r['score']}: {r['text'][:80]}...")
        if not res: print("  [WARN] no results (data may not be ready)")
