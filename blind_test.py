"""blind_test.py - Phase 2: Blind role identification test framework
Generates unlabeled debate fragments for human evaluation (>80% identifiability target)"""
import json, random
from pathlib import Path

def generate_blind_test():
    """Extract debate fragments, strip agent labels, create test sheet"""
    sessions_dir = Path("E:/debate-arena/sessions")
    
    # Collect fragments from real debates
    fragments = []
    for f in sessions_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            for turn in data.get("turns", []):
                content = turn.get("content","").strip()
                # Skip error/failed turns
                if "BadRequestError" in content or "Authentication Fails" in content:
                    continue
                if "沉思中" in content:
                    continue
                if len(content) >= 50 and len(content) <= 500:
                    fragments.append({
                        "text": content,
                        "agent": turn["agent"],
                        "topic": data["topic"][:30]
                    })
        except: pass
    
    if len(fragments) < 15:
        print(f"[WARN] Only {len(fragments)} fragments, need 15+ for valid test")
        return
    
    # Select 15 diverse fragments (5 per agent)
    selected = []
    for agent in ["zhuangzi","nietzsche","beauvoir"]:
        agent_frags = [f for f in fragments if f["agent"] == agent]
        if len(agent_frags) >= 5:
            selected.extend(random.sample(agent_frags, 5))
    
    random.shuffle(selected)
    
    # Create test sheet (for human evaluator)
    print("=== Blind Role Identification Test ===\n")
    print("Instructions: Read each fragment and identify which philosopher said it.\n")
    print(f"Fragments: {len(selected)}\n")
    
    for i, f in enumerate(selected):
        print(f"[{i+1}] {f['text'][:200]}")
        print(f"    Topic: {f['topic']}")
        print(f"    Your guess (庄周/尼采/波伏娃): ___")
        print()
    
    # Answer key (separate)
    print("="*40)
    print("ANSWER KEY (for evaluator only)")
    print("="*40)
    for i, f in enumerate(selected):
        name = {"zhuangzi":"庄周","nietzsche":"尼采","beauvoir":"波伏娃"}.get(f["agent"],"未知")
        print(f"[{i+1}] {name}")
    
    # Save
    test_data = {"fragments":[{"id":i+1,"text":f["text"][:300],"topic":f["topic"]} for i,f in enumerate(selected)],
                  "answer_key":[{"id":i+1,"agent":f["agent"]} for i,f in enumerate(selected)]}
    with open(sessions_dir / "blind_test.json",'w',encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {sessions_dir / 'blind_test.json'}")

if __name__ == "__main__":
    generate_blind_test()
