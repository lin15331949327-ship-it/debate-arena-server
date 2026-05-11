"""chunk.py - Phase 1-1: Semantic text chunking (500-1000 chars, 50 char overlap)"""
import re, json
from pathlib import Path
import jieba

DOCS = Path("E:/debate-arena/knowledge/docs")

def is_cn(text): return sum(1 for c in text if '\u4e00'<=c<='\u9fff')/max(len(text),1)

def word_count(text):
    if is_cn(text) > 0.3: return len(text)
    return len(text.split())

def chunk_text(text, source, min_sz=500, max_sz=1000, overlap=50):
    if is_cn(text) < 0.3: min_sz, max_sz = 300, 600
    
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    if len(paragraphs) <= 1:
        paragraphs = [p.strip() for p in re.split(r'(?<=[.?!。！？])\s*', text) if p.strip()]
    
    chunks, current = [], ""
    for para in paragraphs:
        test = current + ("\n" if current else "") + para
        if word_count(test) <= max_sz:
            current = test
        else:
            if current and word_count(current) >= min_sz:
                chunks.append({"text":current,"source":source,"chunk_id":f"{source}_{len(chunks):04d}"})
                prev = current.split('\n')
                ov = ""
                for p in reversed(prev):
                    if word_count(p+"\n"+ov if ov else p) > overlap: break
                    ov = p + ("\n"+ov if ov else "")
                current = (ov+"\n"+para) if ov else para
            else:
                for sent in re.split(r'(?<=[.?!。！？])', para):
                    sent = sent.strip()
                    if not sent: continue
                    t2 = current + sent
                    if word_count(t2) <= max_sz: current = t2
                    else:
                        if current and word_count(current) >= min_sz:
                            chunks.append({"text":current,"source":source,"chunk_id":f"{source}_{len(chunks):04d}"})
                        current = sent
    
    if current.strip() and word_count(current) >= 50:
        chunks.append({"text":current,"source":source,"chunk_id":f"{source}_{len(chunks):04d}"})
    return chunks

def chunk_agent(agent):
    orig = DOCS / agent / "original"
    if not orig.exists():
        print(f"  [SKIP] {agent}: no original/ dir"); return []
    
    all_chunks = []
    for fp in sorted(orig.glob("*.txt")):
        if fp.name.startswith("chunk_"): continue
        src = fp.stem
        with open(fp,'r',encoding='utf-8') as f: text = f.read()
        chunks = chunk_text(text, src)
        for c in chunks:
            (orig / f"{c['chunk_id']}.txt").write_text(c['text'], encoding='utf-8')
        all_chunks.extend(chunks)
        print(f"  {src}: {len(chunks)} chunks")
    
    meta = DOCS / agent / "chunks_metadata.json"
    with open(meta,'w',encoding='utf-8') as f: json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    print(f"  [DONE] {agent}: {len(all_chunks)} total chunks")
    return all_chunks

if __name__ == "__main__":
    print("=== Phase 1-1: Semantic Chunking ===\n")
    for agent in ["zhuangzi","nietzsche","beauvoir"]:
        print(f"--- {agent} ---")
        chunks = chunk_agent(agent)
