# 🎭 三才辩场 — 三Agent跨时空思想辩论场

> 庄子(🦋) × 尼采(⚡) × 波伏娃(👁️) — DeepSeek驱动的跨时空对话

## 运行

```bash
cd E:\debate-arena
python run.py -t "自由是什么？" -k YOUR_DEEPSEEK_KEY -r 3
```

## 项目结构

```
debate-arena/
├── agents/prompts.py    # 三Agent系统提示词(庄子/尼采/波伏娃)
├── knowledge/base.py    # 知识库(各15条核心文本)
├── engine/debate.py     # 辩论引擎(状态机+回合调度)
├── run.py               # 主程序
└── sessions/            # 辩论记录存档
```
