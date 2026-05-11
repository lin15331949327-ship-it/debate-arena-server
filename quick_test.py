import sys, os, requests, time
sys.path.insert(0, "E:/debate-arena")
from agents.prompts import AGENT_PROMPTS
from search import search

k = os.environ.get("DEEPSEEK_API_KEY", "")
print("Test: zhuangzi answers a question...")
kb = search("zhuangzi", "自由是什么", 3)
print(f"KB: {len(kb)} results")

r = requests.post("https://api.deepseek.com/chat/completions",
    headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
    json={"model": "deepseek-chat",
          "messages": [{"role": "system", "content": AGENT_PROMPTS["zhuangzi"]},
                       {"role": "user", "content": "问题: 自由是什么"}],
          "max_tokens": 200, "temperature": 0.7},
    timeout=60)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    d = r.json()
    ans = d["choices"][0]["message"]["content"]
    print(f"Answer ({len(ans)} chars):")
    print(ans[:300])
else:
    print(r.text[:300])
