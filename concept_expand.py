"""concept_expand.py - Phase 1-6: Core concept graph expansion"""
import json
from pathlib import Path

DOCS = Path("E:/debate-arena/knowledge/docs")

FULL_CONCEPTS = {
    "zhuangzi": {
        "core_concepts": [
            {"name": "道", "desc": "宇宙本原和最高真理，无形无名，无为而无不为", "source": "大宗师/齐物论"},
            {"name": "齐物", "desc": "万物平等，以道观之物无贵贱，超越是非对立", "source": "齐物论"},
            {"name": "逍遥", "desc": "心灵不受外物所累的精神自由，无待于外", "source": "逍遥游"},
            {"name": "无为", "desc": "不强行作为，顺应自然之道", "source": "应帝王"},
            {"name": "无用之用", "desc": "世人眼中的无用恰恰是最大的用处", "source": "人间世"},
            {"name": "物化", "desc": "万物形态之间的转化，如梦蝶，生死不过形态变化", "source": "齐物论"},
            {"name": "心斋", "desc": "虚静心的状态，超越感官和理性认知", "source": "人间世"},
            {"name": "坐忘", "desc": "堕肢体、黜聪明、离形去知、同于大通", "source": "大宗师"},
            {"name": "天籁", "desc": "万物自然而然的声音，非人为分别", "source": "齐物论"},
            {"name": "混沌", "desc": "日凿一窍七日而死——秩序杀死了本真", "source": "应帝王"},
            {"name": "庖丁解牛", "desc": "以神遇不以目视，依天理——技艺臻于道", "source": "养生主"},
            {"name": "濠梁之辩", "desc": "子非鱼安知鱼之乐——认知边界与主体间性", "source": "秋水"},
            {"name": "相忘江湖", "desc": "相濡以沫不如相忘于江湖", "source": "大宗师"},
            {"name": "以道观之", "desc": "以道观之物无贵贱，视角决定价值", "source": "秋水"},
            {"name": "吾丧我", "desc": "超越自我中心的小我，达到与天地合一", "source": "齐物论"},
        ],
        "argument_patterns": ["寓言故事法","反问消解法","视角转换法","悖论揭示法","类比扩展法","归谬法"],
        "blind_spots": ["过度相对化导致价值虚无","消解一切判断失去行动基础","回避具体处境和历史责任","逍遥可能成为特权者的遁词"],
        "relationships": [
            {"from":"道","to":"齐物","rel":"从道观之则万物齐一"},
            {"from":"齐物","to":"逍遥","rel":"认识到万物齐一才能逍遥"},
            {"from":"逍遥","to":"无用之用","rel":"无用即是逍遥的体现"},
            {"from":"心斋","to":"坐忘","rel":"心斋是坐忘的方法"},
            {"from":"物化","to":"混沌","rel":"物化是自然，混沌死是非自然"},
        ]
    },
    "nietzsche": {
        "core_concepts": [
            {"name":"权力意志","desc":"一切生命的本质是自我超越和增强的意志","source":"查拉图斯特拉/善恶的彼岸"},
            {"name":"超人","desc":"人是一种应当被超越的东西，价值的自我创造者","source":"查拉图斯特拉如是说"},
            {"name":"永恒轮回","desc":"如果生命无限重复，你是否能对每一刻说是","source":"查拉图斯特拉/快乐的科学"},
            {"name":"上帝已死","desc":"传统道德的形而上学基础崩塌，人必须自己创造价值","source":"快乐的科学/查拉图斯特拉"},
            {"name":"主人道德vs奴隶道德","desc":"主人道德来自自我肯定，奴隶道德来自怨恨","source":"道德的谱系"},
            {"name":"酒神精神","desc":"醉的狂欢、生命的肯定、混沌中的创造力","source":"悲剧的诞生"},
            {"name":"日神精神","desc":"梦的幻象、秩序、个体化原理、美的外观","source":"悲剧的诞生"},
            {"name":"末人","desc":"没有渴望、没有创造、只求安逸舒适的平庸之人","source":"查拉图斯特拉如是说"},
            {"name":"深渊","desc":"当你凝视深渊时深渊也在凝视你——自我认识的危险","source":"善恶的彼岸"},
            {"name":"价值重估","desc":"对所有传统价值进行彻底重新评估","source":"偶像的黄昏/敌基督"},
            {"name":"爱命运(Amor Fati)","desc":"热爱命运，不只是接受而是想要——对一切说是","source":"瞧这个人/快乐的科学"},
            {"name":"精神三变","desc":"骆驼->狮子->孩子：承担->反抗->创造新价值","source":"查拉图斯特拉如是说"},
            {"name":"怨恨(Ressentiment)","desc":"弱者的报复心理，把无力变成道德优越","source":"道德的谱系"},
            {"name":"视角主义","desc":"没有事实只有解释，一切认知都是特定视角的产物","source":"遗稿"},
            {"name":"舞蹈的星辰","desc":"你必须携带混沌才能生出舞蹈的星辰","source":"查拉图斯特拉如是说"},
        ],
        "argument_patterns":["宣言式断言法","挑衅反问法","格言爆破法","历史谱系学法","隐喻攻击法","自我矛盾法"],
        "blind_spots":["过度个体化忽视结构压迫","美化权力可能导致暴政辩护","反体系导致自相矛盾","精英主义忽视弱者处境"],
        "relationships":[
            {"from":"上帝已死","to":"价值重估","rel":"上帝死后必须重估一切价值"},
            {"from":"权力意志","to":"超人","rel":"超人是对权力意志的最高肯定"},
            {"from":"超人","to":"永恒轮回","rel":"只有肯定永恒轮回的人才是超人"},
            {"from":"酒神精神","to":"爱命运","rel":"酒神精神是对命运全然的肯定"},
            {"from":"主人道德","to":"奴隶道德","rel":"对立：自我肯定vs怨恨报复"},
        ]
    },
    "beauvoir": {
        "core_concepts": [
            {"name":"存在先于本质","desc":"人不是被给定的本质而是不断自我塑造的存在","source":"存在主义"},
            {"name":"处境(Situation)","desc":"自由不是抽象的，在具体历史处境中被限制或展开","source":"第二性/模糊性的伦理学"},
            {"name":"他者(The Other)","desc":"女人被定义为相对于男人的第二性——他者化","source":"第二性卷一"},
            {"name":"成为女人","desc":"女人不是天生的而是后天形成的——性别是社会建构","source":"第二性卷二"},
            {"name":"模糊性伦理","desc":"人类存在既是主体又是客体的根本模糊性","source":"模糊性的伦理学"},
            {"name":"内在性vs超越性","desc":"女人被封闭在内在性中，男人获得超越性","source":"第二性"},
            {"name":"解放","desc":"不是独善其身而是所有人的共同事业","source":"第二性/模糊性的伦理学"},
            {"name":"命名即揭示","desc":"要解放必须首先命名压迫——让不可见的变成可见的","source":"第二性"},
            {"name":"生物学不是命运","desc":"女性的生物性差异被文化解释为劣势但非必然","source":"第二性卷一"},
            {"name":"神话与实在","desc":"关于女人的神话掩盖了真实的女人处境","source":"第二性卷一"},
            {"name":"具体自由","desc":"自由不在别处就在于每天的具体行动中","source":"模糊性的伦理学"},
            {"name":"相互承认","desc":"真正的爱情应建立在两个自由人的相互承认之上","source":"第二性"},
            {"name":"客体化","desc":"当人放弃自由就变成物——被他人定义","source":"第二性"},
            {"name":"压迫者的依赖","desc":"压迫者不会因不公正而放弃压迫除非被压迫者反抗","source":"第二性"},
            {"name":"代际传递","desc":"女人被教导成为客体却一直怀着主体的渴望","source":"第二性卷二"},
        ],
        "argument_patterns":["解构常识法","处境分析法","层层剥开法","具体追问法","历史谱系法","反诘法"],
        "blind_spots":["过度结构归因可低估个体能动性","二元框架可能简化性别多样性","早期作品忽略种族和阶级交叉性"],
        "relationships":[
            {"from":"处境","to":"存在先于本质","rel":"存在先于本质但处境先于选择"},
            {"from":"他者","to":"成为女人","rel":"被定义为他者，后天形成为第二性"},
            {"from":"内在性vs超越性","to":"解放","rel":"从内在性走向超越性就是解放之路"},
            {"from":"命名即揭示","to":"解放","rel":"命名是解放的第一步"},
            {"from":"模糊性伦理","to":"具体自由","rel":"在模糊性中通过具体行动实现自由"},
        ]
    }
}

if __name__ == "__main__":
    print("=== Phase 1-6: Concept Graph Expansion ===\n")
    for agent in ["zhuangzi","nietzsche","beauvoir"]:
        ana_dir = DOCS / agent / "analysis"
        ana_dir.mkdir(parents=True, exist_ok=True)
        concepts = FULL_CONCEPTS[agent]
        
        with open(str(ana_dir / "core_concepts.json"), 'w', encoding='utf-8') as f:
            json.dump(concepts["core_concepts"], f, ensure_ascii=False, indent=2)
        with open(str(ana_dir / "argument_patterns.json"), 'w', encoding='utf-8') as f:
            json.dump({"patterns":concepts["argument_patterns"],"blind_spots":concepts["blind_spots"]}, f, ensure_ascii=False, indent=2)
        with open(str(ana_dir / "relationships.json"), 'w', encoding='utf-8') as f:
            json.dump(concepts["relationships"], f, ensure_ascii=False, indent=2)
        
        print(f"  [OK] {agent}: {len(concepts['core_concepts'])} concepts, {len(concepts['argument_patterns'])} patterns, {len(concepts['relationships'])} relations")
    
    print("\n[DONE] Concept graphs expanded")
