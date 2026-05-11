"""Extract Zhuangzi epub - deep inspection approach"""
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup
import re, base64, io, zipfile
import html

EPUB = Path("E:/debate-arena/knowledge/[新编诸子集成]庄子集释(上) ([清]郭庆藩撰王孝鱼 点校) (z-library.sk, 1lib.sk, z-lib.sk).epub")

# Open as zip to inspect
with zipfile.ZipFile(EPUB, 'r') as zf:
    names = zf.namelist()
    print(f"Total files in epub: {len(names)}")
    
    # Show structure
    for n in names[:30]:
        info = zf.getinfo(n)
        print(f"  {info.file_size:>8}B  {n}")
    
    if len(names) > 30:
        print(f"  ... and {len(names)-30} more")
    
    # Find html/xhtml files
    html_files = [n for n in names if n.endswith(('.html','.xhtml','.htm'))]
    print(f"\nHTML/XHTML files: {len(html_files)}")
    for hf in html_files[:10]:
        info = zf.getinfo(hf)
        print(f"  {info.file_size:>8}B  {hf}")
    if len(html_files) > 10:
        print(f"  ... and {len(html_files)-10} more")
    
    # Try reading a sample HTML file
    for hf in html_files[:3]:
        content = zf.read(hf)
        text = content.decode('utf-8', errors='replace')
        soup = BeautifulSoup(text, 'html.parser')
        body_text = soup.get_text('\n', strip=True)
        print(f"\n--- {hf} ({len(body_text)} chars) ---")
        print(body_text[:500])
