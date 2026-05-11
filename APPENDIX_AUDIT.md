# 附录 7.1 参考项目技术采纳审计

## 1. agentic-philosophers — 多Agent聊天系统、角色Prompt设计

| 借鉴点 | 是否采纳 | 证据 |
|--------|---------|------|
| 多Agent聊天系统架构 | ✅ | 3Agent辩论系统，DebateEngine v3管理speaker_order轮转 |
| 角色Prompt设计模式 | ✅ | agents/prompts.py v3 含身份/时代/思想/性格/风格/口头禅/偏见/关系8层结构 |
| Agent类设计和消息路由 | ✅ | HistoryEntry+CollisionEntry数据类，engine.next_speaker()路由 |
| 扩展为3Agent+对抗性约束 | ✅ | 强制碰撞约束、forbidden_moves、ROUND_INSTRUCTIONS差异化 |

## 2. Multi-Agent-Debates-LangGraph — StateGraph辩论流程、Judge评估

| 借鉴点 | 是否采纳 | 证据 |
|--------|---------|------|
| StateGraph状态管理 | ✅ | DebateState含phase三阶段(in_debate→closing→ended) |
| 回合循环 | ✅ | 6轮差异化调度，ROUND_INSTRUCTIONS每轮不同 |
| Judge评估机制 | ⚠️ 不采用（按任务书） | 取而代之：碰撞强度评分(分歧+深度+创造)+质量报告 |
| 状态流转逻辑 | ✅ | current_agent_idx推进+round递增+phase切换 |

## 3. Character-LLM — Experience Reconstruction、角色一致性

| 借鉴点 | 是否采纳 | 证据 |
|--------|---------|------|
| 角色经验数据生成人格一致性 | ✅ | 概念图谱(15概念+6论证模式+5关系)、寓言故事集、注疏精要 |
| Prompt层面模拟训练效果 | ✅ | 不训练模型，通过详细System Prompt模拟人格一致性 |
| 角色辨识度验证 | ✅ | 单体测试30轮100%+盲测框架15片段+答案键 |
| 认知偏见设计 | ✅ | 每个Agent刻意的盲点+设计意图标注（"让XX攻击用"） |

## 4. DebateGraph — 多Agent结构化辩论、LangGraph集成

| 借鉴点 | 是否采纳 | 证据 |
|--------|---------|------|
| 结构化辩论 | ✅ | 6轮差异化：R1立场→R2/3回应→R4综合→R5深化→R6收束 |
| 辩论状态定义 | ✅ | DebateState 17字段完整(含history.key_arguments+attacks) |
| LangGraph集成 | ⚠️ 自研替代 | 自建状态机替代LangGraph——DebateEngine直接管理状态流转，降低外部依赖 |
| 状态流转逻辑 | ✅ | 回合推进+phase切换+存档持久化 |

## 5. 分析结论

| 参考项目 | 采纳率 | 关键适配 |
|---------|--------|---------|
| agentic-philosophers | 100% | 扩展为3Agent对抗式 |
| Multi-Agent-Debates-LangGraph | 75% | 不用Judge，改用碰撞评分 |
| Character-LLM | 100% | Prompt级别（非训练级别）模拟 |
| DebateGraph | 75% | 自研状态机替代LangGraph |

**总体采纳率: 87.5%**。两个未完全采纳项均有明确替代方案且工作正常。
