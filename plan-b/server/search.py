"""search.py - Phase 1-5: Qdrant Cloud vector retrieval"""
import os, json, requests

QDRANT_URL = os.environ.get("QDRANT_URL", "")
QDRANT_KEY = os.environ.get("QDRANT_API_KEY", "")
EMBED_API_KEY = os.environ.get("SILICONFLOW_API_KEY")
if not EMBED_API_KEY:
    import sys
    print("[WARN] SILICONFLOW_API_KEY 未设置，向量检索将跳过", file=sys.stderr)
    # 不 exit，让调用方降级处理；调用方 _get_embedding 返回 None 降级
COLLECTION = "debate_knowledge"

HEADERS = {"api-key": QDRANT_KEY, "Content-Type": "application/json"}

# ═══════════════════════════════════════════════════════════
# 查询扩展 — 弥补 BGE-M3 跨时代/跨语言语义鸿沟
# ═══════════════════════════════════════════════════════════
QUERY_EXPANSION = {
    # 庄子体系
    "自由": "自由 逍遥 无待 鲲鹏 物化 齐物 自然",
    "幸福": "幸福 至乐 天乐 逍遥 养生",
    "死亡": "死亡 物化 气化 安时而处顺 鼓盆而歌",
    "自然": "自然 无为 天道 逍遥 齐物",
    "自我": "自我 吾丧我 真君 天籁 无己",
    # 尼采体系
    "权力": "权力 权力意志 主人道德 超人 自我超越",
    "痛苦": "痛苦 深渊 克服 永恒轮回 悲剧",
    "道德": "道德 奴隶道德 主人道德 善恶 价值重估",
    "欲望": "欲望 权力意志 升华 酒神 本能",
    "虚无": "虚无 上帝已死 积极虚无主义 末人 价值重建",
    "命运": "命运 爱命运 Amor Fati 永恒轮回 必然",
    # 波伏娃体系
    "平等": "平等 他者 第二性 处境 解放 主体",
    "性别": "性别 第二性 处境 成为女人 存在先于本质",
    "存在": "存在 本质 处境 他者 主体间性 自由",
    "责任": "责任 他者 处境 自由 伦理 主体",
    # 跨体系通用
    "真理": "真理 解释 视角主义 谎言 求真意志",
    "孤独": "孤独 深渊 超人 末人 走钢索 逍遥 离群",
    "意义": "意义 永恒轮回 虚无 荒谬 存在先于本质 价值 创造",
    "身体": "身体 肉身 大地 本能 处境",
}

def expand_query(query):
    """模糊匹配：query 包含扩展键中的任一关键词时，拼接对应扩展词"""
    expanded = set()
    for keyword, terms in QUERY_EXPANSION.items():
        if keyword in query:
            for t in terms.split():
                if t not in query:  # 避免重复已在 query 中的词
                    expanded.add(t)
    if expanded:
        return f"{query} {' '.join(expanded)}"
    return query

def _get_embedding(text):
    """Get BGE-M3 embedding from SiliconFlow"""
    r = requests.post("https://api.siliconflow.cn/v1/embeddings",
        json={"model": "BAAI/bge-m3", "input": [text], "encoding_format": "float"},
        headers={"Authorization": f"Bearer {EMBED_API_KEY}", "Content-Type": "application/json"},
        timeout=30)
    if r.status_code != 200:
        return None
    return r.json()["data"][0]["embedding"]

def search_agent_knowledge(agent, query, top_k=5):
    """Search Qdrant for agent-specific knowledge chunks"""
    # 查询扩展：弥补 BGE-M3 跨时代语义鸿沟
    expanded_query = expand_query(query)
    vec = _get_embedding(expanded_query)
    if not vec:
        return []

    payload = {
        "vector": vec,
        "limit": top_k,
        "with_payload": True,
        "filter": {
            "must": [{"key": "agent", "match": {"value": agent}}]
        }
    }

    r = requests.post(
        f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
        headers=HEADERS, json=payload, timeout=15
    )

    if r.status_code != 200:
        return []

    results = []
    for pt in r.json().get("result", []):
        text = pt.get("payload", {}).get("text", "")
        # 修复：payload.text 可能是 Python dict repr（数据上传时序列化了整个字典）
        # 例如 "{'id': '寓言故事集_0000', 'source': '寓言故事集', 'text': '实际内容...'}"
        if isinstance(text, str) and text.startswith("{") and "'text':" in text:
            try:
                import ast
                parsed = ast.literal_eval(text)
                if isinstance(parsed, dict):
                    text = parsed.get("text", text)
            except (ValueError, SyntaxError):
                pass
        results.append({
            "chunk_id": str(pt.get("id", "")),
            "text": text,
            "source": f"{agent}/vector_store",
            "score": round(pt.get("score", 0), 4),
            "method": "QDRANT"
        })
    return results

def search(agent, query, top_k=5):
    return [r["text"] for r in search_agent_knowledge(agent, query, top_k)]

def enrich_context(agent, topic, base):
    """[已弃用] RAG 检索已移至 bridge.py 独立查询，此函数保留用于调试"""
    relevant = search(agent, f"{topic} {base}", top_k=3)
    if not relevant:
        return base
    return "## 相关原文\n" + "\n".join(f"> {r}" for r in relevant) + "\n\n" + base

if __name__ == "__main__":
    for agent in ["zhuangzi", "nietzsche", "beauvoir"]:
        print(f"--- {agent} ---")
        res = search_agent_knowledge(agent, "自由", top_k=3)
        for i, r in enumerate(res):
            print(f"  [{i+1}] {r['method']} s={r['score']}: {r['text'][:80]}...")
        if not res:
            print("  [WARN] no results")
