import os, re

# Fix bridge.py path
path = "E:/debate-arena/plan-b/server/bridge.py"
c = open(path, 'r', encoding='utf-8').read()
c = c.replace('sys.path.insert(0, "E:/debate-arena")',
              'sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))')
open(path, 'w', encoding='utf-8').write(c)
print("bridge.py: path fixed")

# Fix search.py paths (if hardcoded)
spath = "E:/debate-arena/plan-b/server/search.py"
if os.path.exists(spath):
    sc = open(spath, 'r', encoding='utf-8').read()
    sc = sc.replace("E:/debate-arena/knowledge", 
                     "os.path.join(os.path.dirname(os.path.abspath(__file__)), 'knowledge')")
    open(spath, 'w', encoding='utf-8').write(sc)
    print("search.py: path fixed")

# Verify the fix works
import sys
sys.path.insert(0, "E:/debate-arena/plan-b/server")
from engine.debate import DebateEngine
from agents.prompts import AGENT_PROMPTS
print("Import test: OK")
