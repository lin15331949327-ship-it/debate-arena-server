# 🏛️ Three-Agent Debate Arena

> **Zhuangzi · Nietzsche · Beauvoir — AI-powered philosophical collision across 2,400 years**
>
> Three complete systems of thought, three AI Agents, one question. Daoism, Will to Power, and Existentialism clash, counter, and illuminate each other — simultaneously.

## ✨ What This Is

A multi-agent debate engine where **Zhuangzi** (Daoism, 4th century BCE), **Nietzsche** (Will to Power, 19th century), and **Beauvoir** (Existentialism & Feminism, 20th century) — each armed with their full corpus of writings — debate the same philosophical question across 6 structured rounds. Every response is grounded in a 2,601-document knowledge base via Qdrant vector search.

The engine schedules differentiated behaviors per round (stance → response → synthesis → deepening), detects intellectual collisions between agents, scores debate quality, and exports publishable Markdown transcripts.

## 🎭 Sample Output

> Topic: **"What if you meet someone better — but there's a previous lover?"** — Round 3, Beauvoir:

**Beauvoir**

你们二位——一位要求人"用血痕在岩石上作画"，一位劝诫"让系统如四季更替般朽坏"——你们看似对立，实则共同回避了同一个血腥的现实：**血痕会被清洗，而四季更替中，有人正在冻毙**。

尼采，你赞美绝境中的意志——但那位试图用血作画的女性，她的手指可能根本触碰不到岩石。她的身体首先被规训、被监视、被定义为"应当安静地等待"。这不是意志的强弱问题，而是**权力如何具体地限制了身体行动的可能性**。

庄子，你"春风化雪"的比喻同样危险。历史上无数女性就在"自然朽坏"的哲学中耗尽了一生——因为系统在"自然"地将她们的才华化为雪水，滋养下一代男性的庄园。

你们都谈论"自由"，但尼采的自由是特权者的勋章，庄子的自由是旁观者的幻觉。真正的解放始于一个简单、却令人不适的事实：**在改变处境之前，有些人连"选择"的语法都不被允许掌握。**

## 🛠 Tech Stack

| Layer | Tech |
|-------|------|
| LLM | Xiaomi MiMo V2.5 Pro (Token Plan) |
| Engine | Python · 6-round scheduling · Collision detection · Quality scoring |
| Knowledge | Qdrant Cloud · 2,601 indexed texts · BGE-M3 embeddings |
| Frontend | 5 PWA themes (Liquid Glass, Tenebrism, Epistolary, Frost White, Visual Novel) |
| Real-time | Node.js + Socket.IO · Railway |
| Deploy | Cloudflare Pages (frontend) + Railway (backend) |

## 🚀 Quick Start

```bash
git clone https://github.com/lin15331949327-ship-it/debate-arena-server
cd debate-arena-server
cp .env.example .env
# Edit .env with your API keys

pip install requests

# Local 3-round test
python test_run.py "What is freedom?" 3

# Full 6-round debate
python test_run.py "Does suffering have meaning?" 6

# Export to publishable Markdown
python export_md.py sessions/test_20260513_161226.json

# Quality analysis
python analyze.py --recent 10
```

## ⚠️ AI Disclaimer

All debate content is AI-generated. It does not represent the actual views of Zhuangzi, Nietzsche, or Beauvoir, nor the project author's positions. AI interpretation of philosophical texts has inherent limitations and biases. Generated content is for speculative reference and entertainment only. Do not equate AI-simulated philosophical dialogue with academic research.

---

# 🏛️ 三Agent思想辩论场

> **庄子 · 尼采 · 波伏娃 — 跨越2400年的AI思想碰撞**
>
> 三套完整的思想体系，三个AI Agent，同一个命题。道家、权力意志、存在主义在辩论中互相对抗、互相照亮。

## ✨ 项目简介

一个多Agent辩论引擎。**庄子**（道家，公元前4世纪）、**尼采**（权力意志，19世纪）、**波伏娃**（存在主义与女性主义，20世纪）——各自加载其全部著作的知识库——在6轮结构化辩论中交锋。每轮发言都通过Qdrant向量搜索从2,601条原文索引中检索相关知识。

引擎实现6轮差异化调度（立场声明→回应→综合→深化），检测Agent间的思想碰撞，评估辩论质量，并导出可直接发布的Markdown记录。

## 🎭 效果展示

> 辩题：**"人总会遇到更好的人，但原先的爱人怎么办？"** — 第3轮，波伏娃发言：

**波伏娃**

你们二位——一位要求人"用血痕在岩石上作画"，一位劝诫"让系统如四季更替般朽坏"——你们看似对立，实则共同回避了同一个血腥的现实：**血痕会被清洗，而四季更替中，有人正在冻毙**。

尼采，你赞美绝境中的意志——但那位试图用血作画的女性，她的手指可能根本触碰不到岩石。她的身体首先被规训、被监视、被定义为"应当安静地等待"。这不是意志的强弱问题，而是**权力如何具体地限制了身体行动的可能性**。

庄子，你"春风化雪"的比喻同样危险。历史上无数女性就在"自然朽坏"的哲学中耗尽了一生——因为系统在"自然"地将她们的才华化为雪水，滋养下一代男性的庄园。

你们都谈论"自由"，但尼采的自由是特权者的勋章，庄子的自由是旁观者的幻觉。真正的解放始于一个简单、却令人不适的事实：**在改变处境之前，有些人连"选择"的语法都不被允许掌握。**

## 🛠 技术栈

| 层 | 技术 |
|----|------|
| AI模型 | Xiaomi MiMo V2.5 Pro（Token Plan） |
| 辩论引擎 | Python · 6轮差异化调度 · 碰撞检测 · 质量评分 |
| 知识库 | Qdrant Cloud · 2,601条原文索引 · BGE-M3嵌入 |
| 前端 | 5款PWA主题（液态玻璃·长河光影·思想书简·霜白·次元绘卷） |
| 实时通信 | Node.js + Socket.IO · Railway部署 |
| 部署 | Cloudflare Pages（前端） + Railway（后端） |

## 🚀 三步启动

```bash
git clone https://github.com/lin15331949327-ship-it/debate-arena-server
cd debate-arena-server
cp .env.example .env
# 编辑 .env 填入 API Key

pip install requests

# 本地3轮快速测试
python test_run.py "什么是真正的自由？" 3

# 6轮完整辩论
python test_run.py "痛苦有意义吗？" 6

# 导出为 Markdown（可发布）
python export_md.py sessions/test_20260513_161226.json

# 查看质量分析
python analyze.py --recent 10
```

## 🎨 PWA 主题

| 主题 | 风格 |
|------|------|
| 液态玻璃·臻境 | Apple 式毛玻璃，spring 动画 |
| 长河·光影 | 伦勃朗照明 · 丁达尔效应 |
| 思想书简 | 三种哲学书信气泡 |
| 霜白·臻简 | 极简毛玻璃悬浮卡片 |
| 次元·绘卷 | 视觉小说竖屏，角色立绘 |

在线体验：**[debate-arena-9g2.pages.dev](https://debate-arena-9g2.pages.dev)**

## 📂 项目结构

```
debate-arena/
├── engine/debate.py         # 核心辩论引擎（状态机·碰撞检测·导演模块）
├── agents/prompts.py        # 三Agent系统提示词
├── test_run.py              # 本地测试入口
├── analyze.py               # 辩论质量分析报告
├── export_md.py             # JSON → Markdown 导出
├── plan-b/
│   ├── server/              # Node.js + Socket.IO 后端
│   │   ├── index.js         # Express 服务器
│   │   ├── bridge.py        # Python 辩论引擎桥接
│   │   └── search.py        # Qdrant 云版知识检索
│   └── pwa/                 # 5款 PWA 前端主题
└── knowledge/               # 知识库原始文本
    └── concepts/            # 核心概念映射
```

## ⚠️ AI 标注

本项目所有辩论内容由 AI 自动生成，不代表庄周、尼采、波伏娃本人的真实观点，亦不代表项目作者立场。AI 对哲学文本的理解存在局限和偏差，生成内容仅供思辨参考和娱乐体验。请勿将 AI 模拟的哲学对话等同于学术研究。
