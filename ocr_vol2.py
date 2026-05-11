"""OCR Zhuangzi vol.2 (下)"""
import zipfile, base64, time, sys
from pathlib import Path
import requests

EPUB = Path("E:/debate-arena/knowledge/[新编诸子集成]庄子集释(下) ([清]郭庆藩撰王孝鱼 点校) (z-library.sk, 1lib.sk, z-lib.sk).epub")

def main():
    print("Step 1: Baidu OCR token...", flush=True)
    r = requests.get("https://aip.baidubce.com/oauth/2.0/token",
        params={"grant_type":"client_credentials",
                "client_id":"cU1FVPe08DJzqWw2K4degUo2",
                "client_secret":"lRi6wCvgppdnIdA71ZsRNK3EUTCNlEmZ"}, timeout=10)
    token = r.json().get("access_token","")
    print(f"Token OK", flush=True)
    
    print("Step 2: Extract images...", flush=True)
    imgs = []
    with zipfile.ZipFile(EPUB, 'r') as zf:
        for name in sorted(zf.namelist()):
            if name.endswith('.jpg') and '_1.jpg' in name:
                data = zf.read(name)
                if len(data) > 10000:
                    imgs.append((name, data))
    print(f"  {len(imgs)} pages", flush=True)
    
    print("Step 3: OCR...", flush=True)
    texts = []
    for i, (name, img) in enumerate(imgs):
        b64 = base64.b64encode(img).decode()
        try:
            r = requests.post(f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={token}",
                data={"image":b64}, headers={"Content-Type":"application/x-www-form-urlencoded"}, timeout=30)
            text = "\n".join(w["words"] for w in r.json().get("words_result",[])) if r.status_code==200 else ""
        except: text = ""
        if text and len(text)>20: texts.append(text)
        if (i+1)%10==0 or i==len(imgs)-1:
            print(f"  [{i+1}/{len(imgs)}]", flush=True)
        time.sleep(0.5)
    
    # Append to existing file
    full = "\n\n".join(texts)
    outpath = Path("E:/debate-arena/knowledge/zhuangzi_full.txt")
    existing = outpath.read_text(encoding='utf-8') if outpath.exists() else ""
    outpath.write_text(existing + "\n\n" + full, encoding='utf-8')
    print(f"[DONE] +{len(full)} chars (total: {len(existing)+len(full)})", flush=True)

if __name__ == "__main__":
    main()
