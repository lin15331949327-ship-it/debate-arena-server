"""OCR Zhuangzi epub using Baidu OCR API"""
import zipfile, base64, json, time, re
from pathlib import Path
import requests

EPUB = Path("E:/debate-arena/knowledge/[新编诸子集成]庄子集释(上) ([清]郭庆藩撰王孝鱼 点校) (z-library.sk, 1lib.sk, z-lib.sk).epub")
EPUB2 = Path("E:/debate-arena/knowledge/[新编诸子集成]庄子集释(下) ([清]郭庆藩撰王孝鱼 点校) (z-library.sk, 1lib.sk, z-lib.sk).epub")
OUTPUT = Path("E:/debate-arena/knowledge/zhuangzi_full.txt")

AK = "cU1FVPe08DJzqWw2K4degUo2"
SK = "lRi6wCvgppdnIdA71ZsRNK3EUTCNlEmZ"

def get_token():
    r = requests.get("https://aip.baidubce.com/oauth/2.0/token",
        params={"grant_type":"client_credentials","client_id":AK,"client_secret":SK}, timeout=10)
    return r.json().get("access_token","")

def ocr_image(img_bytes, token):
    b64 = base64.b64encode(img_bytes).decode()
    for attempt in range(3):
        try:
            r = requests.post(
                f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={token}",
                data={"image":b64}, headers={"Content-Type":"application/x-www-form-urlencoded"}, timeout=30)
            if r.status_code == 200:
                words = r.json().get("words_result",[])
                return "\n".join(w["words"] for w in words)
            elif r.status_code == 429:
                time.sleep(2**attempt)
            else:
                time.sleep(1)
        except: time.sleep(2)
    return ""

def extract_and_ocr(epub_path, token, start_idx=0):
    """Extract images from epub, OCR each page"""
    texts = []
    with zipfile.ZipFile(epub_path, 'r') as zf:
        jpgs = sorted([n for n in zf.namelist() if n.endswith('.jpg')])
        total = len(jpgs)
        
        for i, name in enumerate(jpgs):
            if i < start_idx: continue
            
            img = zf.read(name)
            # Skip small images (<10KB = likely decorations)
            if len(img) < 10000:
                continue
            
            print(f"  [{i+1}/{total}] {name} ({len(img)//1024}KB)...", end=" ")
            text = ocr_image(img, token)
            
            if text and len(text) > 20:
                texts.append(text)
                print(f"{len(text)} chars")
            else:
                print("empty/skip")
            
            # Rate limit: 2 QPS for free tier
            time.sleep(0.6)
    
    return texts

if __name__ == "__main__":
    print("Getting Baidu OCR token...")
    token = get_token()
    if not token:
        print("[ERR] Failed to get OCR token")
        exit(1)
    print(f"Token: {token[:20]}...")
    
    all_text = []
    
    for ep in [EPUB, EPUB2]:
        if not ep.exists():
            print(f"[SKIP] {ep.name} not found")
            continue
        print(f"\nOCR: {ep.name}")
        texts = extract_and_ocr(ep, token)
        all_text.extend(texts)
        print(f"  Got {len(texts)} pages, {sum(len(t) for t in texts)} chars")
        # Refresh token every 200 pages
        token = get_token()
    
    full = "\n\n".join(all_text)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(full)
    print(f"\n[DONE] {len(full)} chars saved to {OUTPUT}")
