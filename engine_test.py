"""Quick engine v3 test - no LLM needed, uses mock responses"""
import sys, json
sys.path.insert(0, "E:/debate-arena")
from engine.debate import DebateEngine

# Mock agent responses for a 6-round debate
MOCK_RESPONSES = {
    "zhuangzi": [
        "自由？请循其本——你们在问一条鱼，水是不是牢笼。我昨夜梦见蝴蝶，不知我是庄周还是蝴蝶。你说自由，可连'我是谁'尚且未定，何谈自由？（首发立场）",
        "尼采说我滑溜——确实，泥鳅在泥里是滑的。可你若非要'必须'跳出泥潭，这'必须'二字不又是新的笼子？波伏娃，你说处境——在蝴蝶看来，牢笼和花园有区别吗？（综合回应）",
    ],
    "nietzsche": [
        "哈！庄子——你这条滑溜溜的东方泥鳅！你说自由是笼子？不对！自由不是被给予的选择，而是创造自己法则的能力！大鹏之所以飞九万里，是因为它必须飞——那是它权力意志的自我表达！（回应+立场）",
        "庄子，你的逍遥游不过是逃避深渊！波伏娃，你问'谁来创造'——我告诉你：是每一个敢于说'我是'的人！不是处境决定自由，而是自由的意志创造处境！（深化+攻击）",
    ],
    "beauvoir": [
        "你的论述很迷人——但让我们看看它掩盖了什么。你说女人不是天生的而是后天形成的，自由亦然。庄子的蝴蝶不需要养孩子、不需要面对生育和家务——他的逍遥是特权者的逍遥。尼采的钢索没有安全网——但让我问你一个具体的问题：谁来创造？在什么条件下创造？（回应+立场）",
        "庄子说相忘于江湖——可水已经快干了，忘却只是另一种自杀。尼采说成为自己——你脚下的地基是谁给的？你首先需要一个可以成为自己的处境。没有处境，你的'成为'不过是在真空中挥舞拳头。（最后一击——不是总结，是追问）",
    ],
}

engine = DebateEngine()
engine.start(topic="自由是什么？人真的可以自由吗？", max_rounds=6)

print("=== 6-Round Debate Test (Mock) ===\n")

for r in range(1, 7):
    for agent in engine.state.speaker_order:
        speaker = engine.next_speaker()
        if not speaker or engine.state.phase == "ended":
            break
        
        responses = MOCK_RESPONSES.get(speaker, ["..."])
        idx = min(r-1, len(responses)-1)
        content = responses[idx]
        
        warning = engine.record_turn(speaker, content)
        name = {"zhuangzi":"庄周","nietzsche":"尼采","beauvoir":"波伏娃"}[speaker]
        ri = engine.get_round_instruction()[:30]
        print(f"  R{r} {name}: {content[:60]}...")
        if warning:
            print(f"    [!] {warning}")

# Results
print(f"\n=== Results ===")
print(f"Turns: {len(engine.state.history)}")
print(f"Phase: {engine.state.phase}")

cr = engine.collision_report()
print(f"Collisions: {cr['total']} ({cr.get('by_type',{})})")

qr = engine.quality_report()
print(f"Quality: {qr.get('verdict','?')} (score={qr.get('quality_score',0)})")

# Show history structure
h = engine.state.history[0]
print(f"\nHistoryEntry example: round={h.round} speaker={h.speaker} key_args={h.key_arguments} attacks={h.attacks}")

c = engine.state.collision_log[0] if engine.state.collision_log else None
if c:
    print(f"CollisionEntry example: from={c.from_agent} to={c.to_agent} type={c.collision_type} point={c.point[:40]} intensity={c.intensity}")

print("\n[DONE] Engine v3 verified")
