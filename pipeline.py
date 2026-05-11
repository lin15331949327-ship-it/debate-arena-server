"""pipeline.py - 4-phase debate pipeline: Generate -> Review -> Polish -> Execute"""
import os, json, time, sys
from pathlib import Path
import litellm

sys.path.insert(0, "E:/debate-arena")
from agents.prompts import AGENT_PROMPTS
from engine.debate import DebateEngine
from search import enrich_context

AGENT_NAMES = {"zhuangzi":"庄周","nietzsche":"尼采","beauvoir":"波伏娃"}
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
MODEL = "deepseek/deepseek-chat"

def llm(sys_prompt, user_prompt, max_tokens=800, temp=0.7):
    os.environ["DEEPSEEK_API_KEY"] = API_KEY
    try:
        resp = litellm.completion(
            model=MODEL,
            messages=[{"role":"system","content":sys_prompt},{"role":"user","content":user_prompt}],
            max_tokens=max_tokens, temperature=temp, timeout=120)
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"  [LLM ERR] {e}")
        return ""

def generate_prompt_additions(topic):
    """Phase 1: Generate role-specific prompt additions for the topic"""
    print(f"  [Phase 1] Generating prompt additions...")
    sys_p = """你是辩论提示词设计师。给定话题，为三个思想家各生成一段话题特定的辩论角度提示，每个控制在80字内。\n输出JSON: {"zhuangzi":"...","nietzsche":"...","beauvoir":"..."}"""
    raw = llm(sys_p, f"话题: {topic}")
    try:
        if raw.startswith("```"): raw = raw[raw.index("\n")+1:raw.rindex("```")]
        return json.loads(raw.strip())
    except:
        return {"zhuangzi":"从相对主义和自然之道出发","nietzsche":"从权力意志和自我超越出发","beauvoir":"从处境和结构不平等出发"}

def review_prompts(prompts, topic):
    """Phase 2: Review prompts for collision potential"""
    print(f"  [Phase 2] Reviewing prompts...")
    sys_p = """你是辩论审核师。审视三个角色的提示词，判断他们是否会真正碰撞还是各说各话。\n输出JSON: {"issue":"是否存在趋同风险","suggestion":"改进建议","ok":true/false}"""
    raw = llm(sys_p, f"话题: {topic}\n庄子提示:{prompts.get('zhuangzi','')}\n尼采提示:{prompts.get('nietzsche','')}\n波伏娃提示:{prompts.get('beauvoir','')}")
    try:
        if raw.startswith("```"): raw = raw[raw.index("\n")+1:raw.rindex("```")]
        return json.loads(raw.strip())
    except:
        return {"ok":True,"issue":"","suggestion":""}

def polish_prompts(prompts, feedback, topic):
    """Phase 3: Polish prompts based on review feedback"""
    if feedback.get("ok"): 
        print(f"  [Phase 3] Prompts OK, no polishing needed")
        return prompts
    print(f"  [Phase 3] Polishing: {feedback.get('suggestion','')[:80]}")
    sys_p = """你是提示词打磨师。根据审核意见修改三个角色的辩论角度，增强碰撞性。\n输出JSON: {"zhuangzi":"...","nietzsche":"...","beauvoir":"..."}"""
    raw = llm(sys_p, f"话题: {topic}\n当前提示:{json.dumps(prompts,ensure_ascii=False)}\n改进建议:{feedback.get('suggestion','')}")
    try:
        if raw.startswith("```"): raw = raw[raw.index("\n")+1:raw.rindex("```")]
        return json.loads(raw.strip())
    except:
        return prompts

def agent_speak_enhanced(agent, topic, history, additions):
    """Enhanced agent speaking with RAG context enrichment"""
    base_prompt = AGENT_PROMPTS[agent]
    full_prompt = f"{base_prompt}\n\n## 本场辩论话题\n{topic}\n\n## 话题特定角度\n{additions.get(agent,'')}"
    
    context = history
    # Enrich with knowledge base
    enriched = enrich_context(agent, topic, history)
    if enriched != history: context = enriched
    
    return llm(full_prompt, context, max_tokens=600, temp=0.8)

def run_pipeline_debate(topic, max_rounds=3, first_speaker=None):
    """Full debate pipeline: Generate->Review->Polish->Execute"""
    if not API_KEY:
        return {"error":"DEEPSEEK_API_KEY not set"}
    
    print(f"\n{'='*50}")
    print(f"Pipeline Debate: {topic}")
    print(f"{'='*50}")
    t0 = time.time()
    
    # Phase 1: Generate prompt additions
    additions = generate_prompt_additions(topic)
    
    # Phase 2: Review
    feedback = review_prompts(additions, topic)
    
    # Phase 3: Polish
    additions = polish_prompts(additions, feedback, topic)
    print(f"  Pipeline done in {time.time()-t0:.1f}s")
    
    # Phase 4: Execute debate
    print(f"  [Phase 4] Executing {max_rounds}-round debate...")
    engine = DebateEngine()
    engine.start(topic=topic, max_rounds=max_rounds, first_speaker=first_speaker)
    
    all_turns = []
    for r in range(1, max_rounds+1):
        for agent in engine.state.speaker_order:
            speaker = engine.next_speaker()
            if not speaker or engine.state.phase == "ended": break
            
            history = engine.get_context(for_agent=speaker)
            content = agent_speak_enhanced(speaker, topic, history, additions)
            if not content: content = f"[{AGENT_NAMES[speaker]}思考中...]"
            
            warning = engine.record_turn(speaker, content)
            name = AGENT_NAMES.get(speaker, speaker)
            ri = engine.get_round_instruction()[:40]
            print(f"  R{r} {name}: {content[:60]}...")
            if warning: print(f"    [!] {warning}")
            all_turns.append({"agent":speaker,"name":name,"round":r,"content":content})
    
    report = engine.collision_report()
    quality = engine.quality_report()
    print(f"  Collisions: {report['total']} events | Quality: {quality.get('verdict','?')} ({quality.get('quality_score',0)})")
    
    return {"topic":topic,"turns":all_turns,"collision_report":report,"quality_report":quality,"status":"completed"}
