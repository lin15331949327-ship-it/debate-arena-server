"""preprocess.py - Phase 0-2: Text preprocessing + semantic paragraph segmentation"""
import os, re, json
from pathlib import Path

BASE = Path("E:/debate-arena/knowledge")
DOCS = Path("E:/debate-arena/knowledge/docs")

TEXT_SOURCES = {
    "zhuangzi": {
        "files": [
            ("zhuangzi_full.txt","庄子全文"),
            ("daodejing.txt","道德经"),
            ("daojia_supplement.txt","道家补充"),
        ],
        "commentary_files": [
            ("docs/zhuangzi/commentary/commentary_summary.md","注疏精要"),
            ("docs/zhuangzi/commentary/fables_collection.md","寓言故事集"),
        ],
        "encoding": "utf-8",
    },
    "nietzsche": {
        "files": [
            ("nietzsche_9books.txt","Nietzsche Collected"),
            ("nietzsche_genealogy.txt","Genealogy of Morals"),
            ("nietzsche_twilight.txt","Twilight of the Idols"),
        ],
        "commentary_files": [
            ("docs/nietzsche/commentary/supplementary.md","后世解读与书信"),
        ],
        "encoding": "utf-8",
    },
    "beauvoir": {
        "files": [
            ("beauvoir_second_sex_vol1.txt","The Second Sex Vol.1"),
            ("beauvoir_vol5.txt","The Second Sex Vol.2"),
            ("beauvoir_ethics.txt","Ethics of Ambiguity"),
            ("beauvoir_she_came_to_stay.txt","She Came to Stay"),
            ("beauvoir_memoirs_vol2.txt","Memoirs Vol.2"),
            ("beauvoir_memoirs_vol4.txt","Memoirs Vol.4"),
        ],
        "commentary_files": [
            ("docs/beauvoir/commentary/supplementary.md","萨特与后世女性主义"),
        ],
        "encoding": "utf-8",
    },
}

def clean_text(text: str) -> str:
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'ISBN[\s\d\-Xx]+', '', text)
    text = re.sub(r'\n\s*\d{1,4}\s*\n', '\n', text)
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    text = re.sub(r'[ \t]{3,}', '  ', text)
    return text.strip()

def split_paragraphs(text: str) -> list:
    raw = re.split(r'\n\s*\n', text)
    result = []
    for p in raw:
        p = p.strip()
        if not p: continue
        if len(p) < 30 and not any('\u4e00' <= c <= '\u9fff' for c in p): continue
        result.append(p)
    return result

def preprocess_agent(agent: str):
    sources = TEXT_SOURCES.get(agent, {})
    files = sources.get("files", [])
    commentary_files = sources.get("commentary_files", [])
    enc = sources.get("encoding", "utf-8")
    out_dir = DOCS / agent / "original"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    all_paras = []
    # Process main text files
    for fname, label in files:
        fpath = BASE / fname
        if not fpath.exists():
            print(f"  [SKIP] {fname} not found")
            continue
        try:
            with open(fpath, 'r', encoding=enc) as f:
                text = f.read()
        except:
            for e in ['gbk','gb2312','latin-1']:
                try:
                    with open(fpath, 'r', encoding=e) as f:
                        text = f.read()
                    break
                except: continue
            else:
                print(f"  [FAIL] Cannot decode {fname}")
                continue
        
        text = clean_text(text)
        paras = split_paragraphs(text)
        print(f"  {label}: {len(text)} chars -> {len(paras)} paragraphs")
        
        out_path = out_dir / f"{label}.txt"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(paras))
        all_paras.extend(paras)
    
    # Process commentary/supplementary files
    for fname, label in commentary_files:
        fpath = BASE / fname
        if not fpath.exists():
            print(f"  [SKIP commentary] {fname} not found")
            continue
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                text = f.read()
        except:
            print(f"  [FAIL commentary] Cannot read {fname}")
            continue
        text = clean_text(text)
        paras = split_paragraphs(text)
        print(f"  [commentary] {label}: {len(text)} chars -> {len(paras)} paragraphs")
        out_path = out_dir / f"{label}.txt"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(paras))
        all_paras.extend(paras)
    
    print(f"  [DONE] {agent}: {len(all_paras)} total paragraphs")
    return all_paras

if __name__ == "__main__":
    print("=== Phase 0-2: Text Preprocessing ===\n")
    for agent in ["zhuangzi","nietzsche","beauvoir"]:
        print(f"--- {agent} ---")
        preprocess_agent(agent)
    print("\n[DONE] Preprocessing complete")
