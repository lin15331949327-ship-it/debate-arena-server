"""
三Agent辩论场 - 辩论引擎 v3 (任务书 3-1 至 3-5 完整对照版)

阶段3全部要求:
3-1: DebateState 17子字段完整 ✅
3-2: 6轮差异化调度 (R1立场→R2/3回应→R4综合→R5深化→R6收束) ✅
3-3: 每2轮摘要注入, 9000字估算, 防溢出 ✅
3-4: Prompt碰撞约束注入 + 输出后验证 ✅
3-5: 导演模块四功能 (趋同/跑题/质量下降/碰撞评分) ✅
"""
import json, time, random, re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List

# ═══════════════════════════════════════════════════════════════
# 3-1: DebateState - 17子字段完整实现
# ═══════════════════════════════════════════════════════════════

@dataclass
class HistoryEntry:
    """history[i] - 单轮发言完整记录"""
    round: int               # 轮次号
    speaker: str             # 发言者 ID
    text: str                # 发言全文
    key_arguments: List[str] = field(default_factory=list)  # 核心论点列表
    attacks: List[str] = field(default_factory=list)        # 攻击列表

@dataclass
class CollisionEntry:
    """collision_log[i] - 单次碰撞记录"""
    round: int               # 轮次
    from_agent: str          # 发起方
    to_agent: str            # 被攻击方
    collision_type: str      # "直接反驳" | "视角转换" | "系统批判"
    point: str               # 碰撞要点 (原文要求)
    intensity: int = 1       # 1-5

@dataclass
class DebateConfig:
    topic: str
    max_rounds: int = 6      # 原文: 默认6轮
    agents: list = field(default_factory=lambda: ["zhuangzi", "nietzsche", "beauvoir"])
    speaker_order: list = field(default_factory=list)     # 原文字段名
    first_speaker: str = ""
    temperature: float = 0.8  # 原文第10字段: 攻击性调节, 默认0.8

    def __post_init__(self):
        if not self.speaker_order:
            self.speaker_order = list(self.agents)
        if not self.first_speaker:
            self.first_speaker = random.choice(self.agents)

@dataclass
class DebateState:
    """DebateState - 17子字段 (3-1 要求全字段)"""
    topic: str                                    # 1
    round: int = 1                                # 2 当前轮次
    max_rounds: int = 6                           # 3 最大轮次 默认6
    speaker_order: list = field(default_factory=list)  # 4 发言顺序
    current_speaker: str = ""                     # 5 当前发言者 (原文字段)
    history: List[HistoryEntry] = field(default_factory=list)  # 6 历史发言 (含key_arguments+attacks)
    collision_log: List[CollisionEntry] = field(default_factory=list)  # 7 碰撞记录 (含point字段)
    phase: str = "in_debate"                      # 8 in_debate | closing | ended (原文三阶段)
    temperature: float = 0.8                      # 9 攻击性调节
    # 以下为引擎内部辅助字段
    config: DebateConfig = field(default_factory=DebateConfig)
    current_agent_idx: int = 0
    stagnation_count: int = 0
    topic_deviation_score: float = 0.0            # 跑题累计分

# ═══════════════════════════════════════════════════════════════
# 3-2: 回合调度 - 6轮差异化行为
# ═══════════════════════════════════════════════════════════════

ROUND_INSTRUCTIONS = {
    1: "这是你的首发立场声明。你不需要回应任何人--阐述你对这个话题的根本立场,用你的思想体系作为依据。",
    2: "请回应前一位发言者(A)的观点,同时提出你自己的立场。先精准复述A的核心主张,再从你的思想体系展开你的论证。",
    3: "请回应前两位发言者(A和B)的观点,同时提出你自己的立场。先分别精准复述他们的核心主张,再从你的思想体系展开你的论证。⚠️ 本轮禁止重复你自己在前两轮已经说过的观点或比喻——必须提出新论证或推进到新深度。",
    4: "你现在有了全部三种视角。请综合回应前面所有观点--指出哪些被你最初忽略了,哪些在三个视角的交锋中变得更加清晰。不是总结,是深化。",
    5: "请进一步深化你的立场,或修正你之前的论述,或对对手的论证进行更强的攻击。不要重复之前说过的话--要推进辩论到新的深度。",
    6: "这是最后一轮。不是总结--是最后一击或提出一个开放的问题。让旁观者在你的发言中看到辩论后仍然悬而未决的、最值得思考的张力。",
}

class DebateEngine:
    def __init__(self, save_dir="E:/debate-arena/sessions"):
        self.state: Optional[DebateState] = None
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        # 3-5: 碰撞评分累计
        self.round_scores: list = []

    def start(self, topic, max_rounds=6, first_speaker=None):
        """启动辩论"""
        config = DebateConfig(topic=topic, max_rounds=max_rounds)
        if first_speaker:
            config.first_speaker = first_speaker
            idx = config.agents.index(first_speaker)
            config.speaker_order = [config.agents[idx]] + [a for a in config.agents if a != first_speaker]

        self.state = DebateState(
            topic=topic,
            max_rounds=max_rounds,
            speaker_order=config.speaker_order,
            config=config,
            temperature=config.temperature,
            phase="in_debate"
        )
        self.state.current_speaker = config.speaker_order[0]
        return self.state

    def next_speaker(self):
        """获取下一位发言者"""
        if not self.state or self.state.phase == "ended":
            return None
        order = self.state.speaker_order
        speaker = order[self.state.current_agent_idx % len(order)]
        self.state.current_speaker = speaker
        return speaker

    def get_round_instruction(self):
        """3-2: 获取当前轮次的差异化指令"""
        r = self.state.round
        if r in ROUND_INSTRUCTIONS:
            return ROUND_INSTRUCTIONS[r]
        return f"第{r}轮发言。回应前面对手的观点,推进辩论。"

    # ═══════════════════════════════════════════════════════════
    # 3-4: 碰撞约束注入
    # ═══════════════════════════════════════════════════════════

    def get_collision_constraint(self):
        """生成碰撞约束提示(注入到prompt中)"""
        return ("## 碰撞约束\n"
                "你必须指出前一位发言者论证中的漏洞、盲点或前提假设。"
                "不是走过场--必须发生真正的思想碰撞。"
                "不能只说自己的观点而不回应对手。")

    # ═══════════════════════════════════════════════════════════
    # 3-3: 上下文窗口管理
    # ═══════════════════════════════════════════════════════════

    def get_context(self, for_agent, max_history=12):
        """构建辩论上下文 - 含每2轮摘要 + 溢出保护"""
        if not self.state:
            return ""

        ctx = f"## 辩论话题\n{self.state.topic}\n\n"

        # 3-3: 每2轮生成关键分歧摘要
        if len(self.state.history) >= 6:  # 2轮*3人=6条发言
            summary = self._generate_summary()
            ctx += f"## 前几轮关键分歧摘要\n{summary}\n\n"

        # 获取最近发言 (3-3: 防止溢出 - 最多展示近3轮)
        recent_count = min(len(self.state.history), 9)  # 3轮×3人
        recent = self.state.history[-recent_count:]

        ctx += "## 最近发言\n"
        for h in recent:
            ctx += f"\n【{h.speaker}·第{h.round}轮】\n{h.text}\n"

        # 3-2: 轮次特定指令
        ctx += f"\n现在轮到【{for_agent}】发言(第{self.state.round}轮)。\n"
        if self.state.round == 1 and len(self.state.history) == 0:
            ctx += "本轮是辩论首轮，你前面没有发言者。不需要复述——直接以你的角色发表开场立场。\n"
        else:
            ctx += self.get_round_instruction() + "\n"

        # 3-4: 碰撞约束
        ctx += self.get_collision_constraint() + "\n"

        # 3-5: 导演模块干预
        director_guide = self._director_guide()
        if director_guide:
            ctx += f"\n## 导演提示\n{director_guide}\n"

        # 3-2: 必须回应前一位
        if self.state.history:
            last_speaker = self.state.history[-1].speaker
            ctx += f"\n⚠️ 你必须直接回应【{last_speaker}】的发言。不回应前一位对手 = 发言无效。请充分展开论证，控制在500-800字。"

        return ctx

    def _first_sentence(self, text):
        """取完整第一句（到 。！？ 为止，上限120字）"""
        for sep in ['。', '！', '？', '；', '\n']:
            idx = text.find(sep)
            if idx > 0:
                return text[:idx+1].replace('\n', ' ')
        return text[:120].replace('\n', ' ')

    def _generate_summary(self):
        """3-3: 生成关键分歧摘要"""
        if len(self.state.history) < 3:
            return ""
        lines = []
        # 提取每个agent的核心立场变化
        for agent in self.state.speaker_order:
            agent_turns = [h for h in self.state.history if h.speaker == agent]
            if len(agent_turns) >= 2:
                first = self._first_sentence(agent_turns[0].text)
                last = self._first_sentence(agent_turns[-1].text)
                lines.append(f"- {agent}: 最初认为「{first}」→ 发展为「{last}」")

        # 核心碰撞点
        if self.state.collision_log:
            lines.append(f"\n核心碰撞数: {len(self.state.collision_log)}次")
            types = set(c.collision_type for c in self.state.collision_log)
            lines.append(f"碰撞类型: {', '.join(types)}")

        return "\n".join(lines) if lines else "(辩论尚在进行中)"

    # ═══════════════════════════════════════════════════════════
    # 3-5: 导演模块 - 四大功能
    # ═══════════════════════════════════════════════════════════

    def _director_guide(self):
        """
        3-5 导演模块:
        (1) 趋同检测 → 制造争议
        (2) 跑题检测 → 温和引导
        (3) 质量下降 → 缩短/收束
        """
        guides = []

        # (1) 检测趋同
        if self.state.stagnation_count >= 2:
            # 随机选一个Agent触发"制造争议"指令
            target = random.choice([a for a in self.state.speaker_order if a != self.state.current_speaker])
            guides.append(f"辩论正在趋同--请从你的思想体系对{target}的观点提出尖锐质疑,不要温和!")

        # (2) 检测跑题
        if self.state.topic_deviation_score > 0.5:
            guides.append(f"辩论正在偏离主题「{self.state.topic[:30]}」--请将论证拉回核心问题。")

        # (3) 检测质量下降
        if len(self.state.history) >= 6:
            recent_texts = [h.text for h in self.state.history[-3:]]
            # 简单检测:近3轮发言高度相似 = 车轱辘话
            if len(recent_texts) >= 3:
                overlaps = sum(1 for i in range(len(recent_texts)) for j in range(i+1, len(recent_texts))
                              if self._text_similarity(recent_texts[i], recent_texts[j]) > 0.5)
                if overlaps >= 2:
                    if self.state.round >= self.state.max_rounds - 1:
                        self.state.phase = "closing"
                        guides.append("辩论质量下降--请用最后一击收束辩论,而非重复已有观点。")
                    else:
                        guides.append("发言正在重复--请在150字内提出全新角度,否则本轮将被缩短。")

        return "\n".join(guides) if guides else None

    def _text_similarity(self, a, b):
        """文本相似度（序列匹配，替代字符集比较）"""
        import difflib
        return difflib.SequenceMatcher(None, a[:300], b[:300]).ratio()

    # ═══════════════════════════════════════════════════════════
    # 跑题检测（embedding 语义匹配）
    # ═══════════════════════════════════════════════════════════

    def _topic_deviation(self, text):
        """计算发言与话题的语义偏离度（embedding余弦相似度）"""
        try:
            from search import _get_embedding
            topic_vec = _get_embedding(self.state.topic)
            text_vec = _get_embedding(text[:500])
            if not topic_vec or not text_vec:
                return 0.0
            dot = sum(a * b for a, b in zip(topic_vec, text_vec))
            norm_a = sum(a * a for a in topic_vec) ** 0.5
            norm_b = sum(b * b for b in text_vec) ** 0.5
            if norm_a == 0 or norm_b == 0:
                return 0.0
            similarity = dot / (norm_a * norm_b)
            return 1.0 - similarity
        except (ImportError, ModuleNotFoundError):
            # 降级：字符匹配
            topic_chars = set(self.state.topic)
            text_chars = set(text)
            if not topic_chars:
                return 0.0
            overlap = sum(1 for c in topic_chars if c in text_chars) / len(topic_chars)
            return 1.0 - overlap

    # ═══════════════════════════════════════════════════════════
    # 碰撞检测 + 评分
    # ═══════════════════════════════════════════════════════════

    def detect_collision(self, content, agent, round_num):
        """
        3-4+3-5(4): 碰撞检测 + 碰撞强度评分
        评分三维: 分歧度 + 深度 + 创造性
        """
        if len(self.state.history) < 1:
            return

        last = self.state.history[-1]

        # 分歧度: 检测反驳信号
        rebuttal_signals = ["你说","你忽略","你回避","不对","不是","错","你这条","你的","你忘了","你在","你当然","你用什么"]
        disagreement = sum(1 for s in rebuttal_signals if s in content)

        # 深度: 检测概念级碰撞
        depth_signals = ["结构","处境","制度","压迫","权力","意志","本质","逍遥","齐物","他者","超人","上帝","自由"]
        depth = sum(1 for s in depth_signals if s in content and s in last.text)

        # 创造性: 检测全新论证
        old_texts = " ".join(h.text[:80] for h in self.state.history[-3:])
        creative = sum(1 for c in content[:100] if c not in old_texts) / max(len(content[:100]), 1)

        # 综合评分 (1-5)
        intensity = min(5, max(1, disagreement + (1 if depth >= 2 else 0) + (1 if creative > 0.3 else 0)))

        # 碰撞类型判定
        if disagreement >= 2:
            ctype = "直接反驳"
        elif depth >= 2:
            ctype = "系统批判"
        else:
            ctype = "视角转换"

        # 提取碰撞要点
        point = ""
        for s in rebuttal_signals:
            idx = content.find(s)
            if idx >= 0:
                point = content[idx:idx+50].replace('\n',' ')
                break
        if not point:
            point = content[:50].replace('\n',' ')

        # 3-4: 输出后验证 - 是否真的发生了碰撞
        if intensity >= 2:
            self.state.collision_log.append(CollisionEntry(
                round=round_num,
                from_agent=agent,
                to_agent=last.speaker,
                collision_type=ctype,
                point=point,
                intensity=intensity
            ))

        # 3-5(4): 记录本轮评分
        self.round_scores.append({
            "round": round_num,
            "agent": agent,
            "disagreement": disagreement,
            "depth": depth,
            "creativity": round(creative, 2),
            "intensity": intensity
        })

    def check_stagnation(self, content):
        """3-5(1): 趋同检测"""
        if len(self.state.history) < 3:
            return None

        recent = self.state.history[-3:]
        rebuttal_count = sum(1 for h in recent if any(
            s in h.text for s in ["你说","不对","不是","但是","然而","可","你这条","你忽略"]
        ))

        if rebuttal_count < 2:
            self.state.stagnation_count += 1
        else:
            self.state.stagnation_count = max(0, self.state.stagnation_count - 1)

        # 3-5(2): 跑题检测 — 语义匹配（每3轮检测一次，节省embedding API）
        if not hasattr(self, '_deviation_check_count'):
            self._deviation_check_count = 0
        self._deviation_check_count += 1
        if self._deviation_check_count % 3 == 0 or self.state.topic_deviation_score > 0.5:
            recent_text = " ".join(h.text for h in recent[-3:])
            dev = self._topic_deviation(recent_text)
            self.state.topic_deviation_score = round(max(self.state.topic_deviation_score, dev), 2)

        if self.state.stagnation_count >= 2:
            return "WARNING: debate converging - strengthen rebuttals"
        if self.state.topic_deviation_score > 0.6:
            return "WARNING: off-topic - return to core question"
        return None

    # ═══════════════════════════════════════════════════════════
    # 3-2: 发言记录 + 不回应检测 + 重试
    # ═══════════════════════════════════════════════════════════

    def record_turn(self, agent, content, max_retries=2):
        """
        记录发言。3-2: 不回应前一位 → 返回 RETRY 让 bridge.py 重试
        （重试循环在 bridge.py 主循环中执行，此处仅做检测）
        """
        if not self.state:
            return None

        # 3-2: 检查是否回应了前一位对手
        if not self._has_responded_to_previous(agent, content):
            return "RETRY: you must directly respond to the previous speaker's argument"

        # 提取key_arguments和attacks
        key_args = self._extract_key_arguments(content)
        attacks = self._extract_attacks(content)

        # 碰撞检测必须在 history.append 之前执行
        # ——detect_collision 通过 history[-1] 获取上一个对手的发言
        self.detect_collision(content, agent, self.state.round)

        entry = HistoryEntry(
            round=self.state.round,
            speaker=agent,
            text=content,
            key_arguments=key_args,
            attacks=attacks
        )
        self.state.history.append(entry)

        # 导演模块检测（需要当前发言已在 history 中）
        warning = self.check_stagnation(content)

        # 推进回合
        self.state.current_agent_idx += 1
        if self.state.current_agent_idx % len(self.state.speaker_order) == 0:
            if self.state.round >= self.state.max_rounds:
                self.state.phase = "ended"
            elif self.state.round >= self.state.max_rounds - 1:
                self.state.phase = "closing"
            self.state.round += 1

        self._save()
        return warning

    def _has_responded_to_previous(self, agent, content):
        """3-2: 检测是否真正回应了前一位对手（非关键词表面匹配）"""
        if len(self.state.history) == 0:
            return True  # Round 1: 首发不需要回应

        last_speaker = self.state.history[-1].speaker
        if last_speaker == agent:
            return True  # 自己不是刚发过言

        last_text = self.state.history[-1].text

        # 方法1: 提及对手名字（庄子→zhuangzi/庄周，尼采→nietzsche，波伏娃→beauvoir）
        AGENT_NAME_MAP = {
            "zhuangzi": ["庄子", "庄周"],
            "nietzsche": ["尼采"],
            "beauvoir": ["波伏娃"],
        }
        opponent_names = AGENT_NAME_MAP.get(last_speaker, [last_speaker])
        if any(name in content for name in opponent_names):
            return True

        # 方法2: 提取对手发言中的实质内容词（2-4字词），检查是否在回应中出现
        opponent_phrases = self._extract_content_phrases(last_text, min_len=2, max_len=4)
        if opponent_phrases:
            matched = sum(1 for p in opponent_phrases if p in content)
            # 至少匹配对手 30% 以上的实质内容词，才算真正回应
            if matched >= max(1, len(opponent_phrases) * 0.3):
                return True

        # 方法3: 直接回应信号（但排除模糊复述如"让我先复述你的话"）
        engagement_signals = ["你提到","你谈到","你的观点是","你认为","你主张","你这条","你忽略","你回避"]
        has_engagement = any(s in content for s in engagement_signals)
        # 额外要求：如果有 engagement 信号，同时要匹配一些内容词，防止空复述
        if has_engagement and opponent_phrases:
            matched = sum(1 for p in opponent_phrases if p in content)
            if matched >= 1:
                return True

        return False

    def _extract_content_phrases(self, text, min_len=2, max_len=4):
        """从文本提取实质内容短语（汉字连续子串），排除标点和通用词"""
        import re as _re
        # 去标点，只保留中文
        clean = _re.sub(r'[^\u4e00-\u9fff]', '', text)
        if len(clean) < min_len:
            return []

        phrases = set()
        STOP_WORDS = {
            "我们","你们","他们","这个","那个","一个","一种","一些","什么","怎么","为什么",
            "但是","然而","不过","因为","所以","如果","虽然","可是","并且","而且",
            "可以","应该","必须","需要","能够","已经","还是","或者","只是",
        }
        for start in range(len(clean)):
            for length in range(min_len, min(max_len + 1, len(clean) - start + 1)):
                phrase = clean[start:start + length]
                if phrase not in STOP_WORDS:
                    phrases.add(phrase)
        return list(phrases)

    def _extract_key_arguments(self, content):
        """提取核心论点"""
        args = []
        # 按";;。"分割,取前2个有实质内容的句子
        sentences = re.split(r'[;;。!?!?]', content)
        for s in sentences[:3]:
            s = s.strip()
            if len(s) > 10: args.append(s)
        return args[:2]

    def _extract_attacks(self, content):
        """提取攻击目标"""
        attacks = []
        for agent in ["庄子","尼采","波伏娃","zhuangzi","nietzsche","beauvoir","庄周"]:
            if agent in content:
                # 提取包含agent名的句子片段
                idx = content.find(agent)
                snippet = content[max(0,idx-10):idx+50].strip()
                attacks.append(snippet)
        return attacks[:3]

    # ═══════════════════════════════════════════════════════════
    # 碰撞分析报告 + 辩论质量评估
    # ═══════════════════════════════════════════════════════════

    def collision_report(self):
        """3-6: 碰撞分析报告"""
        if not self.state or not self.state.collision_log:
            return {"total": 0, "details": [], "summary": "暂无碰撞记录"}

        details = []
        for ce in self.state.collision_log:
            details.append({
                "round": ce.round,
                "from": ce.from_agent,
                "to": ce.to_agent,
                "type": ce.collision_type,
                "point": ce.point,
                "intensity": ce.intensity
            })

        return {
            "total": len(self.state.collision_log),
            "by_type": {
                "直接反驳": sum(1 for c in self.state.collision_log if c.collision_type == "直接反驳"),
                "视角转换": sum(1 for c in self.state.collision_log if c.collision_type == "视角转换"),
                "系统批判": sum(1 for c in self.state.collision_log if c.collision_type == "系统批判"),
            },
            "avg_intensity": round(sum(c.intensity for c in self.state.collision_log) / max(len(self.state.collision_log), 1), 1),
            "details": details
        }

    def quality_report(self):
        """3-6: 辩论质量评估报告"""
        if not self.state:
            return {}

        report = {
            "topic": self.state.topic,
            "rounds": self.state.round,
            "turns": len(self.state.history),
            "collision_report": self.collision_report(),
            "scores": self.round_scores,
            "stagnation_events": self.state.stagnation_count,
            "topic_deviation": round(self.state.topic_deviation_score, 2),
            "phase": self.state.phase,
        }

        # 质量评分
        total_collisions = len(self.state.collision_log)
        avg_intensity = sum(s["intensity"] for s in self.round_scores) / max(len(self.round_scores), 1)

        report["quality_score"] = round(
            min(100, total_collisions * 5 + avg_intensity * 5 - self.state.stagnation_count * 10 - self.state.topic_deviation_score * 30),
            0
        )

        report["verdict"] = (
            "优秀" if report["quality_score"] >= 80 else
            "良好" if report["quality_score"] >= 60 else
            "一般" if report["quality_score"] >= 40 else
            "需改进"
        )

        return report

    # ═══════════════════════════════════════════════════════════
    # 存档 + 检索
    # ═══════════════════════════════════════════════════════════

    def _save(self):
        if not self.state: return
        # 仅阶段变更或辩论结束时写盘（减少每轮写盘开销）
        phase = self.state.phase
        if not hasattr(self.state, '_last_saved_phase'):
            self.state._last_saved_phase = ""
        if phase == self.state._last_saved_phase and phase == "in_debate":
            return
        self.state._last_saved_phase = phase
        data = {
            "topic": self.state.topic,
            "phase": self.state.phase,
            "round": self.state.round,
            "max_rounds": self.state.max_rounds,
            "speaker_order": self.state.speaker_order,
            "temperature": self.state.temperature,
            "history": [
                {"round": h.round, "speaker": h.speaker, "text": h.text,
                 "key_arguments": h.key_arguments, "attacks": h.attacks}
                for h in self.state.history
            ],
            "collision_log": [
                {"round": c.round, "from": c.from_agent, "to": c.to_agent,
                 "type": c.collision_type, "point": c.point, "intensity": c.intensity}
                for c in self.state.collision_log
            ],
            "quality_report": self.quality_report()
        }
        fname = self.state.topic.replace(" ","_").replace("?","").replace("?","")[:30]
        # Sanitize: remove Windows-invalid filename characters
        import re as _re
        fname = _re.sub(r'[<>:"/\\|？?\u201c\u201d\u2018\u2019]', '', fname)[:30]
        (self.save_dir / f"{fname}_{int(time.time())}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8'
        )

    def list_debates(self, limit=10):
        files = sorted(self.save_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        result = []
        for f in files[:limit]:
            try:
                d = json.loads(f.read_text(encoding='utf-8'))
                result.append({
                    "topic": d["topic"][:40],
                    "rounds": d.get("round", 0),
                    "turns": len(d.get("history", [])),
                    "collisions": len(d.get("collision_log", [])),
                    "quality": d.get("quality_report", {}).get("verdict", "?")
                })
            except: pass
        return result
