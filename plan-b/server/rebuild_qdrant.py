#!/usr/bin/env python3
"""
重灌 Qdrant debate_knowledge collection 的 embedding。
与现有 search.py 使用相同的 SiliconFlow BGE-M3 API，保证搜索行为一致。
安全策略：先写入临时集合，切换后再删除旧集合。
"""
import ast
import json
import logging
import os
import sys
import time
from typing import List

import requests
from qdrant_client import QdrantClient
from qdrant_client.http import models

# ─── 配置（全部从环境变量读取）──────────────────────
QDRANT_URL = os.environ.get("QDRANT_URL", "https://ddd9feb0-f54d-4371-ad4e-2ed38372f1c2.eu-west-1-0.aws.cloud.qdrant.io")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", "")
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY")
if not SILICONFLOW_API_KEY:
    print("[FATAL] 请设置环境变量 SILICONFLOW_API_KEY", file=sys.stderr)
    sys.exit(1)

COLLECTION_NAME = "debate_knowledge"
NEW_COLLECTION_NAME = f"{COLLECTION_NAME}_new"
EMBED_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024

# 批次大小
EMBED_BATCH_SIZE = 32  # SiliconFlow API 单次最大输入条数（文档建议 ≤32 更稳）
UPLOAD_BATCH_SIZE = 200  # Qdrant upsert 每批条数
MAX_RETRIES = 3  # embedding 请求失败重试次数

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ─── 客户端 ───────────────────────────────────────────
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


# ─── Embedding 工具（批量请求，带重试）────────────────
def _embed_batch(texts: List[str]) -> List[list]:
    """调用 SiliconFlow embedding API，返回与 texts 顺序一致的向量列表"""
    if not texts:
        return []
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(
                "https://api.siliconflow.cn/v1/embeddings",
                json={
                    "model": EMBED_MODEL,
                    "input": texts,
                    "encoding_format": "float",
                },
                headers={
                    "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
                    "Content-Type": "application/json",
                },
                timeout=120,  # 批量可能需要较长时间
            )
            if resp.status_code == 200:
                data = resp.json()
                # 返回顺序与 input 一致
                return [item["embedding"] for item in data["data"]]
            else:
                logger.warning("Embedding API 返回 %d: %s", resp.status_code, resp.text[:200])
        except Exception as e:
            logger.warning("Embedding 请求异常: %s", str(e))
        if attempt < MAX_RETRIES - 1:
            sleep_sec = 2 ** attempt
            logger.info("等待 %ds 后重试...", sleep_sec)
            time.sleep(sleep_sec)
    raise RuntimeError(f"Embedding API 调用失败，已重试 {MAX_RETRIES} 次")


def generate_all_embeddings(texts: List[str]) -> List[list]:
    """批量生成所有文本的 embedding"""
    all_vectors = []
    total = len(texts)
    for start in range(0, total, EMBED_BATCH_SIZE):
        end = min(start + EMBED_BATCH_SIZE, total)
        batch = texts[start:end]
        vectors = _embed_batch(batch)
        all_vectors.extend(vectors)
        logger.info(" embedding 进度: %d/%d", end, total)
    return all_vectors


# ─── 文本提取（与现有数据格式对齐）────────────────────
def extract_text(payload: dict) -> str:
    """
    payload.text 可能是：
    - Python dict repr: "{'id': '...', 'text': '北冥有鱼...'}"
    - JSON dict: '{"text": "..."}'
    - 纯文本: "北冥有鱼..."
    解析后取最可能的文本字段，若无法提取有效文本则返回空字符串。
    """
    raw = payload.get("text", "")
    if not raw:
        return ""

    # 先尝试 ast.literal_eval（Python 字面量）
    try:
        parsed = ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        parsed = None

    # 如果上面失败，尝试 json.loads（双引号 JSON）
    if parsed is None:
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            # 不是任何 dict 表示，当作纯文本直接返回
            return raw

    if isinstance(parsed, dict):
        # 按优先级取有意义的文本字段，且长度 >10 避免取到短 id 之类
        for key in ("text", "content", "body"):
            val = parsed.get(key)
            if isinstance(val, str) and len(val.strip()) > 10:
                return val.strip()
        # 如果 dict 里确实没有长文本，放弃该条（返回空字符串）
        logger.warning("payload.text 为 dict 但无法提取有效文本: %s", raw[:100])
        return ""
    # 其他类型（极少情况）当作纯文本
    return raw


# ─── 导出原集合所有 points ───────────────────────────
def export_all_points() -> List[models.Record]:
    logger.info("导出 collection '%s' 中的所有 points...", COLLECTION_NAME)
    points = []
    offset = None
    while True:
        page, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=500,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        points.extend(page)
        if next_offset is None:
            break
        offset = next_offset
        logger.info(" 已导出 %d 条", len(points))
    logger.info("导出完成，共 %d 条", len(points))
    return points


# ─── 安全写入新集合并切换 ────────────────────────────
def safe_rebuild_collection(points: List[models.Record], vectors: List[list]):
    """
    1. 若 NEW_COLLECTION_NAME 已存在则删除
    2. 创建新集合，创建 payload 索引
    3. 分批 upsert 所有数据
    4. 删除原集合，通过别名切换新集合
    """
    # 清理可能残留的新集合
    try:
        client.delete_collection(NEW_COLLECTION_NAME)
        logger.info("已删除残留的临时集合 '%s'", NEW_COLLECTION_NAME)
    except Exception:
        pass

    # 创建新集合
    client.create_collection(
        collection_name=NEW_COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=EMBED_DIM,
            distance=models.Distance.COSINE,
        ),
    )
    logger.info("创建临时集合 '%s' (dim=%d, 余弦距离)", NEW_COLLECTION_NAME, EMBED_DIM)

    # 建立 payload 索引（agent 字段，与 search.py 一致）
    client.create_payload_index(
        collection_name=NEW_COLLECTION_NAME,
        field_name="agent",
        field_schema=models.PayloadSchemaType.KEYWORD,
    )
    logger.info("已创建 payload 索引: agent")

    # 分批上传
    total = len(points)
    for start in range(0, total, UPLOAD_BATCH_SIZE):
        end = min(start + UPLOAD_BATCH_SIZE, total)
        batch = []
        for pt, vec in zip(points[start:end], vectors[start:end]):
            batch.append(
                models.PointStruct(
                    id=pt.id,
                    vector=vec,
                    payload=pt.payload,  # 保留原有 payload
                )
            )
        client.upsert(collection_name=NEW_COLLECTION_NAME, points=batch)
        logger.info(" 上传进度: %d/%d", end, total)
    logger.info("所有数据已写入临时集合。")

    # 切换：删除原集合，通过别名指向新集合
    try:
        client.delete_collection(COLLECTION_NAME)
        logger.info("已删除原集合 '%s'", COLLECTION_NAME)
    except Exception:
        logger.warning("原集合 '%s' 可能不存在，跳过删除", COLLECTION_NAME)

    # 将原名称作为别名指向新集合
    client.update_collection_aliases(
        change_aliases_operations=[
            models.CreateAliasOperation(
                create_alias=models.CreateAlias(
                    collection_name=NEW_COLLECTION_NAME,
                    alias_name=COLLECTION_NAME,
                )
            )
        ]
    )
    logger.info("别名切换完成：'%s' -> '%s'", COLLECTION_NAME, NEW_COLLECTION_NAME)


# ─── 验证搜索 ─────────────────────────────────────────
def verify_search():
    """用线上一致的 embedding API 测试搜索效果"""
    logger.info("=== 验证搜索 ===")
    test_query = "自由"
    query_vecs = _embed_batch([test_query])
    query_vec = query_vecs[0]

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="agent",
                    match=models.MatchValue(value="zhuangzi"),
                )
            ]
        ),
        limit=3,
    )

    found = False
    for i, hit in enumerate(results):
        text = hit.payload.get("text", "")
        snippet = text[:120] if text else "(空)"
        logger.info(" Top %d (score=%.4f): %s", i + 1, hit.score, snippet)
        if any(kw in snippet for kw in ["鲲鹏", "逍遥", "鲲", "逍遥游"]):
            found = True

    if found:
        logger.info("✅ 验证通过：庄子 + 自由 → 命中鲲鹏/逍遥相关 chunk")
    else:
        logger.warning("⚠️ 验证未命中预期关键词，请检查数据或 embedding 质量。")

    # 快速检查其他 agent
    for agent, kw in [("nietzsche", "超人"), ("beauvoir", "他者")]:
        vec = _embed_batch([kw])[0]
        res = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vec,
            query_filter=models.Filter(
                must=[models.FieldCondition(key="agent", match=models.MatchValue(value=agent))]
            ),
            limit=1,
        )
        if res:
            logger.info(" %s + '%s': score=%.4f, text=%s",
                        agent, kw, res[0].score,
                        res[0].payload.get("text", "")[:80])


# ─── 主流程 ───────────────────────────────────────────
def main():
    # 1. 导出原数据
    points = export_all_points()
    if not points:
        logger.error("原集合没有数据，终止。")
        sys.exit(1)

    # 2. 提取真实文本
    texts = [extract_text(pt.payload) for pt in points]
    empty_count = sum(1 for t in texts if not t)
    if empty_count:
        logger.warning("有 %d 条记录提取不到有效文本，将被过滤", empty_count)

    # 3. 过滤空文本（保留对应 point）
    valid_data = [(pt, t) for pt, t in zip(points, texts) if t.strip()]
    if not valid_data:
        logger.error("没有有效文本，退出。")
        sys.exit(1)

    valid_points = [item[0] for item in valid_data]
    valid_texts = [item[1] for item in valid_data]
    logger.info("有效记录数: %d / %d", len(valid_texts), len(texts))
    if len(valid_texts) < len(texts):
        logger.info("已过滤掉 %d 条空文本记录", len(texts) - len(valid_texts))

    # 4. 生成新 embedding（批量 API）
    logger.info("开始生成 embedding（共 %d 条）...", len(valid_texts))
    vectors = generate_all_embeddings(valid_texts)

    # 5. 安全写入并切换集合
    safe_rebuild_collection(valid_points, vectors)

    # 6. 验证
    verify_search()

    logger.info("✅ 全部完成！现在集合 '%s' 已使用新的 BGE-M3 embedding。", COLLECTION_NAME)


if __name__ == "__main__":
    main()
