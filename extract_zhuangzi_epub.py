"""extract_zhuangzi_epub.py — Extract Zhuangzi full text from Guo Qingfan's 庄子集释 epub"""
import re
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup

EPUB_DIR = Path("E:/debate-arena/knowledge")
OUTPUT = EPUB_DIR / "zhuangzi_full.txt"

def extract_text_from_epub(epub_path):
    """Extract all text from epub, organized by chapter"""
    book = epub.read_epub(str(epub_path))
    
    chapters = []
    for item in book.get_items():
        if item.get_type() != 9:  # ITEM_DOCUMENT
            continue
        content = item.get_content()
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text('\n', strip=True)
        if text and len(text) > 100:
            chapters.append(text)
    
    return chapters

def main():
    all_text = []
    
    # Find epub files
    epubs = sorted(EPUB_DIR.glob("*庄子*.epub"))
    if not epubs:
        print("[ERR] No Zhuangzi epub found!")
        return
    
    print(f"Found {len(epubs)} epub files:")
    for ep in epubs:
        print(f"  {ep.name} ({ep.stat().st_size/1024/1024:.0f}MB)")
    
    for ep_path in epubs:
        print(f"\nExtracting: {ep_path.name}...")
        chapters = extract_text_from_epub(ep_path)
        print(f"  Got {len(chapters)} sections, {sum(len(c) for c in chapters)} total chars")
        
        for i, ch in enumerate(chapters):
            # Clean up
            ch = re.sub(r'\n{3,}', '\n\n', ch)
            ch = re.sub(r'[ \t]{3,}', '  ', ch)
            
            # Try to identify chapter boundaries
            ch_title = re.search(r'(内篇|外篇|雜篇|杂篇).*?(第[一二三四五六七八九十]+)', ch)
            if ch_title:
                marker = f"\n\n{'='*60}\n{ch_title.group(0)}\n{'='*60}\n\n"
            else:
                marker = f"\n\n{'─'*40}\nSection {i+1}\n{'─'*40}\n\n"
            
            all_text.append(marker + ch)
    
    # Write output
    full_text = "\n".join(all_text)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    print(f"\n[DONE] Saved {len(full_text)} chars to {OUTPUT}")
    
    # Count chapters
    nei = len(re.findall(r'內篇|内篇', full_text))
    wai = len(re.findall(r'外篇', full_text))
    za = len(re.findall(r'雜篇|杂篇', full_text))
    print(f"  Inner chapters: {nei}, Outer: {wai}, Miscellaneous: {za}")

if __name__ == "__main__":
    main()
