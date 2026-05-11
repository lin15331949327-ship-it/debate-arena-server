"""OCR Zhuangzi epub v2 - simple, reliable"""
import zipfile, base64, time, sys
from pathlib import Path
import requests

EPUB = Path("E:/debate-arena/knowledge/[新编诸子集成]庄子集释(上) ([清]郭庆藩撰王孝鱼 点校) (z-library.sk, 1lib.sk, z-lib.sk).epub")
OUTPUT = Path("E:/debate-arena/knowledge/zhuangzi_full.txt")

def main():
    print("Step 1: Get Baidu OCR token...", flush=True)
    r = requests.get("https://aip.baidubce.com/oauth/2.0/token",
        params={"grant_type":"client_credentials",
                "client_id":"cU1FVPe08DJzqWw2K4degUo2",
                "client_secret":"lRi6wCvgppdnIdA71ZsRNK3EUTCNlEmZ"}, timeout=10)
    token = r.json().get("access_token","")
    if not token:
        print("[ERR] No token:", r.json()); return
    print(f"Token OK: {token[:20]}...", flush=True)
    
    print("Step 2: Extract images from epub...", flush=True)
    imgs = []
    with zipfile.ZipFile(EPUB, 'r') as zf:
        jpgs = sorted([n for n in zf.namelist() if n.endswith('.jpg') and '_1.jpg' in n])
        total = len(jpgs)
        print(f"  Found {total} main pages", flush=True)
        
        for i, name in enumerate(jpgs):
            data = zf.read(name)
            if len(data) < 10000: continue
            imgs.append((name, data))
    print(f"  {len(imgs)} pages to OCR", flush=True)
    
    print("Step 3: OCR each page...", flush=True)
    texts = []
    for i, (name, img) in enumerate(imgs):
        b64 = base64.b64encode(img).decode()
        try:
            r = requests.post(
                f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={token}",
                data={"image":b64}, headers={"Content-Type":"application/x-www-form-urlencoded"}, timeout=30)
            if r.status_code == 200:
                words = r.json().get("words_result",[])
                text = "\n".join(w["words"] for w in words)
            else:
                text = ""
        except:
            text = ""
        
        if text and len(text) > 20:
            texts.append(text)
            status = f"{len(text)} chars"
        else:
            status = "skip"
        
        if (i+1) % 10 == 0 or i == len(imgs)-1:
            print(f"  [{i+1}/{len(imgs)}] {name}: {status}", flush=True)
        time.sleep(0.5)
    
    print(f"\nStep 4: Save results...", flush=True)
    full = "\n\n".join(texts)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(full)
    print(f"[DONE] {len(full)} chars -> {OUTPUT}", flush=True)

if __name__ == "__main__":
    main()
