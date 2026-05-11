# 三Agent思想辩论场 — 技术架构文档

## 系统全景

```
飞书 → /debate命令 → feishu_handler.py
                         │
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
    debate_feishu.py  pipeline.py  单Agent直接调用
           │             │
           ▼             ▼
     DebateEngine v3 (engine/debate.py)
           │
    ┌──────┼──────┐
    ▼      ▼      ▼
  庄周    尼采   波伏娃  (agents/prompts.py)
   │      │      │
   └──────┼──────┘
          ▼
    search.py (BM25+FAISS 混合检索)
          │
          ▼
    SiliconFlow bge-m3 向量库 (767→2601 chunks)
```

## 组件说明

### 1. 知识库层 (knowledge/)
- **文本**: 庄子90万字(OCR epub)、尼采100万字、波伏娃45万字
- **分块**: 2601个语义块，每块500-1000字，50字重叠
- **向量化**: SiliconFlow BAAI/bge-m3，1024维
- **索引**: FAISS IndexFlatIP + BM25混合检索，RRF融合排序
- **概念层**: 每Agent 15核心概念+6论证模式+5概念关系

### 2. Agent层 (agents/prompts.py)
- 庄子: 道家/齐物/逍遥，15概念，6论证模式
- 尼采: 权力意志/超人/永恒轮回，15概念，6论证模式  
- 波伏娃: 存在主义/他者/处境，15概念，6论证模式
- 每个Prompt含: 身份+时代背景+思想体系+性格画像+语言风格+
  口头禅+认知偏见(含设计意图)+与其他Agent关系+三角坐标+知识库指南+辩论硬约束

### 3. 引擎层 (engine/debate.py v3)
- 6轮差异化调度 (R1立场→R2/3回应→R4综合→R5深化→R6收束)
- 碰撞检测(三维评分: 分歧度+深度+创造性)
- 导演模块: 趋同/跑题/质量下降/碰撞评分
- 上下文管理: 每2轮摘要注入，防溢出
- 不回应检测+重试

### 4. 接口层 (feishu_handler.py + debate_feishu.py)
- 4条命令: /debate /debate_status /debate_history /debate_rounds
- 格式化输出: 颜色/标记/角色名/emoji区分

## 性能指标

| 指标 | 当前值 | 说明 |
|------|--------|------|
| KB检索延迟 | ~0.5s | jieba分词+BM25+FAISS |
| 单Agent响应 | 5-7s | DeepSeek API |
| 6轮辩论总计 | ~6min | 18次LLM调用 |
| 知识库加载 | ~1s | jieba词库缓存 |
| 上下文窗口 | <5000字 | 近3轮+摘要 |

## 维护手册

### 重启流程
1. 确认 DEEPSEEK_API_KEY 环境变量已设置
2. 确认 SiliconFlow API Key 在 embed.py 中
3. 飞书中测试: /debate test

### 添加新话题
- 编辑 stress_test.py 的 TOPICS 列表
- 或直接通过飞书 /debate 命令输入

### 更新知识库
1. 添加新文本到 knowledge/*.txt
2. 运行: python preprocess.py && python chunk.py && python embed.py && python build_index.py
3. 运行: python test_search.py 验证
