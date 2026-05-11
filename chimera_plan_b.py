"""
chimera_plan_b.py — 用 Project Chimera 管线推进三Agent辩论场方案B落地
方案B目标: P2 深度体验层 (Web辩论室 + 碰撞热力图 + 旁观者提问 + 多人旁观)

Chimera管线: Phase 0 → Phase 1 → Phase 1.5 → Phase 2
"""
import os, json, time, sys, requests
from pathlib import Path

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"

def call_ds(sys_p, user_p, mt=1500, temp=0.6):
    r = requests.post(API_URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": MODEL, "messages": [{"role":"system","content":sys_p},{"role":"user","content":user_p}],
              "max_tokens": mt, "temperature": temp}, timeout=120)
    return r.json()["choices"][0]["message"]["content"].strip() if r.status_code == 200 else f"[ERR {r.status_code}]"

# ═══════════════════════════════════════════════
# 输入: 方案A现状 + 方案B目标
# ═══════════════════════════════════════════════

STATUS_A = """
三Agent辩论场方案A已完成:
- 3个完整System Prompt (庄子/尼采/波伏娃，各含8层结构)
- 知识库: 2601个语义块，FAISS+BM25混合检索，100%准确率
- 辩论引擎v3: 6轮差异化调度，碰撞检测+导演模块，质量评估
- 飞书集成: /debate等4条命令，格式化输出
- 检索测试22/22(100%)，单体测试30/30(100%)，压力测试10/10(100%)
- 5+场真实辩论记录(sessions/)
- 方案A目前通过飞书消息流展示辩论内容

待实施方案B (任务书P2深度体验):
P2-1: 碰撞分析报告 — 每场辩论后生成碰撞分析
P2-2: Web辩论室 — 独立Web界面，角色头像+风格化排版+实时滚动
P2-3: 碰撞热力图 — 可视化三个Agent在不同话题上的交互强度和分歧模式
P2-4: 知识库扩展 — 支持用户为Agent添加新知识来源
P2-5: 旁观者提问 — 用户在辩论中插入追问
P2-6: 多人旁观模式 — 多用户在飞书群中同时旁观一场辩论
"""

TASK_BOOK_P2 = """
任务书P2功能清单:
- Web辩论室技术方案: Streamlit或Next.js，含Tailwind CSS
- 三个角色各有专属配色和头像
- 辩论内容以轮次式卡片展示
- 碰撞热力图用ECharts/D3.js渲染
- 历史档案可按话题/时间/角色筛选
- 后端API复用现有引擎(DebateEngine v3)
- 用户可通过界面输入新话题或追问
"""

# ═══════════════════════════════════════════════
# Phase 0: Digital Twin — 结构化任务书
# ═══════════════════════════════════════════════
print("="*60)
print("Project Chimera → 三Agent辩论场 方案B 落地计划")
print("="*60)

print("\n[Phase 0] Digital Twin — 生成方案B任务书...")
t0 = time.time()

twin_sys = """你是项目架构师(Digital Twin)。基于方案A现状和方案B目标，生成一份Web辩论室落地方案。
包含: 技术栈推荐(前端框架/图表库/部署方式)、功能优先级(P0/P1)、文件结构、实施步骤(每步原子化)、与现有引擎的集成方式、风险点。
输出Markdown。"""
twin_raw = call_ds(twin_sys, f"## 方案A现状\n{STATUS_A}\n\n## 方案B目标\n{TASK_BOOK_P2}", mt=2000)
print(f"  任务书: {len(twin_raw)} chars ({time.time()-t0:.0f}s)")

# ═══════════════════════════════════════════════
# Phase 1: Dual Research — 技术调研 + UX分析
# ═══════════════════════════════════════════════
print("\n[Phase 1] Dual Research Agents...")

# R1: 技术调研
t1 = time.time()
r1_sys = """你是技术调研专家。基于任务书推荐技术栈。
输出Markdown: 推荐前端框架(含理由+备选)、图表库对比、部署方案、同类项目参考、已知风险。"""
r1_raw = call_ds(r1_sys, f"任务书:\n{twin_raw[:2000]}", mt=1200)
print(f"  R1 技术调研: {len(r1_raw)} chars ({time.time()-t1:.0f}s)")

# R2: UX/竞品分析
t2 = time.time()
r2_sys = """你是UX分析专家。分析多Agent辩论界面的最佳实践。
输出Markdown: 界面布局建议、角色视觉设计、交互流程、无障碍考虑。"""
r2_raw = call_ds(r2_sys, f"任务书:\n{twin_raw[:1500]}\n\n参考: 目标是让用户旁观三个哲学家辩论，界面需要沉浸感。", mt=1200)
print(f"  R2 UX分析: {len(r2_raw)} chars ({time.time()-t2:.0f}s)")

# ═══════════════════════════════════════════════
# Phase 1.5: Skeleton Generation
# ═══════════════════════════════════════════════
print("\n[Phase 1.5] Skeleton Generation...")
t15 = time.time()
skel_sys = """你是项目骨架设计师。基于技术调研生成项目文件结构和依赖清单。
输出: 目录树 + requirements.txt + 核心文件说明。"""
skel_raw = call_ds(skel_sys, f"技术调研:\n{r1_raw[:1500]}\n\nUX分析:\n{r2_raw[:1000]}", mt=1000)
print(f"  骨架: {len(skel_raw)} chars ({time.time()-t15:.0f}s)")

# ═══════════════════════════════════════════════
# Phase 2: Planner + Reviewer
# ═══════════════════════════════════════════════
print("\n[Phase 2] Planner → Reviewer...")

# Planner
tp = time.time()
plan_sys = """你是项目规划师。综合所有研究结果，生成完整的方案B实施方案。
包含: 最终技术栈确认、详细实施步骤(每步原子化+预估工时)、API设计、与现有引擎的集成方案、测试计划。"""
plan_raw = call_ds(plan_sys, f"任务书:\n{twin_raw[:1500]}\n\n技术调研:\n{r1_raw[:1200]}\n\nUX分析:\n{r2_raw[:1200]}\n\n项目骨架:\n{skel_raw[:1000]}", mt=2000)
print(f"  Planner: {len(plan_raw)} chars ({time.time()-tp:.0f}s)")

# Reviewer
tr = time.time()
rev_sys = """你是项目审核师。审核规划师的方案，补充遗漏，修正问题。关注: 与现有引擎集成性、实施可行性、前后端接口设计、部署复杂度。最多提5条修改。输出最终版方案。"""
rev_raw = call_ds(rev_sys, f"原始方案:\n{plan_raw[:2000]}", mt=2000)
final = rev_raw or plan_raw
print(f"  Reviewer: {len(final)} chars ({time.time()-tr:.0f}s)")

# ═══════════════════════════════════════════════
# 保存
# ═══════════════════════════════════════════════
out = f"""# 三Agent辩论场 — 方案B 落地计划 (Project Chimera 生成)

> 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
> Chimera管线: Phase 0 Digital Twin → Phase 1 Dual Research → Phase 1.5 Skeleton → Phase 2 Planner+Reviewer

---

## Phase 0: 结构化任务书
{twin_raw}

## Phase 1: 技术调研
{r1_raw}

## Phase 1: UX/竞品分析
{r2_raw}

## Phase 1.5: 项目骨架
{skel_raw}

## Phase 2: 最终实施方案
{final}
"""

out_path = Path("E:/debate-arena/PLAN_B_CHIMERA.md")
out_path.write_text(out, encoding='utf-8')
print(f"\n[DONE] Saved: {out_path} ({len(out)} chars)")
