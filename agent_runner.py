"""agent_runner.py - Phase 2: formulate_response (3-step: KB search -> analyze opponent -> generate)"""
import sys, os
sys.path.insert(0, "E:/debate-arena")
from agents.prompts import AGENT_PROMPTS
from search import search_agent_knowledge
import requests

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"

def formulate_response(agent, topic, opponent_arguments, debate_history):
    """
    formulate_response 三步流程（对应任务书 2-7）：
    1. 从知识库检索相关思想资源 (top_k=5)
    2. 分析对手论证中的可攻击点
    3. 生成回复（带角色约束）
    """
    # Step 1: KB search
    kb_results = search_agent_knowledge(agent, topic + " " + opponent_arguments, top_k=5)
    kb_text = ""
    if kb_results:
        kb_text = "## 可引用的思想资源\n" + "\n".join(
            f"> [{r['source']}] {r['text'][:200]}" for r in kb_results[:5]
        )
    
    # Step 2: Build attack analysis context
    attack_context = f"""## 辩论话题
{topic}

## 对手论证（你需要回应）
{opponent_arguments}

{kb_text}

## 辩论历史
{debate_history if debate_history else '（首轮，无历史）'}

## 你的任务
先理解对手观点，找到可攻击的弱点（盲点、逻辑漏洞、未审视的前提），然后从你的思想体系内部调用相关资源进行回应。"""
    
    # Step 3: Generate response with role constraints
    prompt = AGENT_PROMPTS[agent]
    
    r = requests.post(API_URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": MODEL,
              "messages": [{"role": "system", "content": prompt},
                           {"role": "user", "content": attack_context}],
              "max_tokens": 500, "temperature": 0.8},
        timeout=90)
    
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"].strip()
    return f"[ERR {r.status_code}]"

def quick_single_test(agent, question):
    """Single-agent quick test via formulate_response"""
    return formulate_response(agent, question, "", "")

if __name__ == "__main__":
    print("=== formulate_response Quick Test ===\n")
    for agent in ["zhuangzi","nietzsche","beauvoir"]:
        r = quick_single_test(agent, "什么是好的生活？")
        print(f"--- {agent} ---")
        print(r[:250])
        print()
