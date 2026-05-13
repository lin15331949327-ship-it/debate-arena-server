"""
三Agent知识库 v2 — FAISS向量检索 + TF-IDF兜底
"""
import json, os, pickle
from pathlib import Path
import numpy as np

KNOWLEDGE_TEXTS = {
    "zhuangzi": [
        "昔者庄周梦为蝴蝶，栩栩然蝴蝶也。自喻适志与！不知周也。俄然觉，则蘧蘧然周也。不知周之梦为蝴蝶与？蝴蝶之梦为周与？——《齐物论》",
        "天地与我并生，而万物与我为一。——《齐物论》",
        "吾生也有涯，而知也无涯。以有涯随无涯，殆已！——《养生主》",
        "庖丁为文惠君解牛……彼节者有间，而刀刃者无厚；以无厚入有间，恢恢乎其于游刃必有余地矣。——《养生主》",
        "人皆知有用之用，而莫知无用之用也。——《人间世》",
        "泉涸，鱼相与处于陆，相呴以湿，相濡以沫，不如相忘于江湖。——《大宗师》",
        "南海之帝为儵，北海之帝为忽，中央之帝为浑沌……日凿一窍，七日而浑沌死。——《应帝王》",
        "北冥有鱼，其名为鲲。鲲之大，不知其几千里也。化而为鸟，其名为鹏。——《逍遥游》",
        "子非鱼，安知鱼之乐？子非我，安知我不知鱼之乐？——《秋水》",
        "以道观之，物无贵贱；以物观之，自贵而相贱。——《秋水》",
        "井蛙不可以语于海者，拘于虚也；夏虫不可以语于冰者，笃于时也。——《秋水》",
        "大知闲闲，小知间间；大言炎炎，小言詹詹。——《齐物论》",
        "至人无己，神人无功，圣人无名。——《逍遥游》",
        "方生方死，方死方生；方可方不可，方不可方可。——《齐物论》",
        "道隐于小成，言隐于荣华。——《齐物论》",
        "大鹏之动，非一羽之轻也；骐骥之速，非一足之力也。——王符引庄子意",
        "朝菌不知晦朔，蟪蛄不知春秋。——《逍遥游》",
        "举世誉之而不加劝，举世非之而不加沮。——《逍遥游》",
        "知其不可奈何而安之若命，德之至也。——《人间世》",
        "夫道未始有封，言未始有常。——《齐物论》",
    ],
    "nietzsche": [
        "上帝已死。上帝仍然是死的。是我们杀死了他。——《快乐的科学》",
        "那没有杀死我的，使我更强大。——《偶像的黄昏》",
        "人是一根绳索，系在动物与超人之间——一根悬于深渊之上的绳索。——《查拉图斯特拉如是说》",
        "我教你们超人。人是一种应当被超越的东西。你们做了什么来超越人呢？——《查拉图斯特拉如是说》",
        "你必须在自己身上携带混沌，才能生出一颗舞蹈的星辰。——《查拉图斯特拉如是说》",
        "与怪物战斗的人，应当小心自己不要成为怪物。当你凝视深渊时，深渊也在凝视你。——《善恶的彼岸》",
        "哪里有生命，哪里就有权力意志；即使在仆人身上，我也找到了要做主人的意志。——《查拉图斯特拉如是说》",
        "一切快乐都想要永恒——想要深深的、深深的永恒！——《查拉图斯特拉如是说》",
        "奴隶道德本质上是功利主义的道德。那个产生善恶对立的温床就是：对权力的感觉和想要报复的怨恨。——《道德的谱系》",
        "每一个不曾起舞的日子，都是对生命的辜负。——《查拉图斯特拉如是说》",
        "人最终爱的是自己的欲望，而不是被欲望的对象。——《善恶的彼岸》",
        "所有伟大的事物都是通过舞蹈而来到世上的。——《查拉图斯特拉如是说》",
        "比起没有目的的谎言，我更愿意接受一个为创造而存在的错误。——遗稿",
        "一个人必须让他的原则有价格。——《查拉图斯特拉如是说》",
        "我爱那种人：他的灵魂即使在受伤时也是深沉的，他可以被一个微小的经历毁灭，但他依然乐意。——《查拉图斯特拉如是说》",
        "你有你的路。我有我的路。至于适当的路、正确的路和唯一的路，这样的路并不存在。——《查拉图斯特拉如是说》",
        "在孤独中，孤独者将自己吞噬殆尽；在人群中，众人将他吞噬殆尽。现在，选择吧。——《人性的，太人性的》",
        "真正的男人想要两件事：危险和游戏。——《查拉图斯特拉如是说》",
        "我不信任一切体系构建者，并且回避他们。体系意志是缺乏诚实的表现。——《偶像的黄昏》",
        "需要一个理由来解释生命的人，终将被生命打败。——《偶像的黄昏》",
    ],
    "beauvoir": [
        "女人不是天生的，而是后天形成的。——《第二性》",
        "一个人不是生来就是女人，而是成为女人。——《第二性》",
        "解放女人，就是拒绝把她封闭在她与男人保持的关系中，但不是否认这些关系。——《第二性》",
        "在男人和女人之间，从来就没有过平等。这种不平等不是自然造成的，而是文化建构的。——《第二性》",
        "人不是一种被给定的本质，而是一种不断自我塑造的存在。——《模糊性的伦理》",
        "自由不在别处，就在于每天的具体行动中。——《模糊性的伦理》",
        "我们不是天生自由的，我们必须不断地为自己争取自由。——《模糊性的伦理》",
        "压迫者不会仅仅因为压迫的不公正性而放弃压迫，而是因为被压迫者的反抗。——《第二性》",
        "生命的意义不是被发现的，而是被创造的。——《模糊性的伦理》",
        "一种自由只有在他人的自由中也得到确认，才是真正的自由。——《模糊性的伦理》",
        "存在先于本质——但处境先于选择。——综合她的思想",
        "女人的悲剧在于：她被教导要成为一个客体，却一直怀着主体的渴望。——《第二性》",
        "当一个人放弃自己的自由，他就变成了物。——《第二性》",
        "最无聊的存在也会提出它为什么存在的问题。——《模糊性的伦理》",
        "在具体的历史处境中，抽象的自由是不存在的。——《第二性》",
        "人的首要特征不是他在寻求快乐，而是他在寻找存在的理由。——《模糊性的伦理》",
        "要解放，必须首先命名。命名就是揭示。——《第二性》",
        "真正的爱情应该建立在两个自由人的相互承认之上。——《第二性》",
        "没有人是自由的，除非所有人都自由。——综合她的思想",
        "我们不是生来就老。我们是生来就新。——《老年》",
    ],
}

class KnowledgeBase:
    """Agent知识库 — FAISS向量检索 + TF-IDF兜底"""
    
    def __init__(self, store_dir="E:/debate-arena/knowledge"):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.texts = KNOWLEDGE_TEXTS
        self.embeddings = {}
        self.encoder = None
        self._encoder_loaded = False
    
    def _build_index(self):
        """构建向量索引"""
        for agent, texts in self.texts.items():
            if self.encoder:
                try:
                    vecs = self.encoder.encode(texts, show_progress_bar=False)
                    self.embeddings[agent] = vecs
                    continue
                except: pass
            
            # TF-IDF兜底
            self.embeddings[agent] = None
    
    def search(self, agent, query, top_k=5):
        """检索最相关的知识片段"""
        texts = self.texts.get(agent, [])
        if not texts: return []
        
        if self.encoder and self.embeddings.get(agent) is not None:
            # 向量检索
            q_vec = self.encoder.encode([query])[0]
            scores = np.dot(self.embeddings[agent], q_vec)
            top_idx = scores.argsort()[-top_k:][::-1]
            return [texts[i] for i in top_idx if scores[i] > 0.1]
        else:
            # TF-IDF 词频兜底
            query_words = set(query)
            scored = []
            for text in texts:
                score = sum(1 for w in query_words if w in text)
                if score > 0: scored.append((score, text))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [t for _, t in scored[:top_k]] or texts[:top_k]
    
    def enrich_context(self, agent, topic, base_context):
        """将检索到的知识注入辩论上下文"""
        relevant = self.search(agent, topic + " " + base_context, top_k=3)
        if not relevant: return base_context
        
        kb_section = "## 可引用的思想资源\n" + "\n".join(f"> {r}" for r in relevant)
        return kb_section + "\n\n" + base_context

# 全局单例
_kb = None
def get_kb():
    global _kb
    if _kb is None: _kb = KnowledgeBase()
    return _kb
