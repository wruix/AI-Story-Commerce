"""AI Story Commerce — 剧本评分与筛选机制

实现 6 维度评分体系：
| 评分维度   | 权重  |
| ------ | --- |
| 前3秒吸引力 | 20% |
| 故事新颖度  | 20% |
| 冲突与反转  | 20% |
| 商品自然植入 | 20% |
| 人物表现力  | 10% |
| 广告合规性  | 10% |

这个评分只作为内部创意筛选工具，不代表真实广告转化预测。
"""

from typing import Any, Dict, List, Optional, Tuple

SCORING_DIMENSIONS = [
    {"name": "前3秒吸引力", "weight": 0.20, "description": "钩子是否足够强，能否在3秒内抓住注意力"},
    {"name": "故事新颖度", "weight": 0.20, "description": "是否避免重复套路，有无独特角度"},
    {"name": "冲突与反转", "weight": 0.20, "description": "剧情冲突是否充分，反转是否出人意料又在情理之中"},
    {"name": "商品自然植入", "weight": 0.20, "description": "商品是否自然融入剧情，不生硬"},
    {"name": "人物表现力", "weight": 0.10, "description": "人物是否鲜活，台词是否符合人设"},
    {"name": "广告合规性", "weight": 0.10, "description": "是否符合广告法，无虚假宣传"},
]


def compute_weighted_score(dimension_scores: Dict[str, float],
                           weights: Optional[Dict[str, float]] = None) -> float:
    """计算加权总分。

    输入：
        dimension_scores: 各维度原始分（0-100）
        weights: 各维度权重，默认使用标准权重
    输出：
        加权总分（0-100）
    """
    if weights is None:
        weights = {d["name"]: d["weight"] for d in SCORING_DIMENSIONS}

    total = 0.0
    total_weight = 0.0
    for dim in SCORING_DIMENSIONS:
        name = dim["name"]
        if name in dimension_scores:
            total += dimension_scores[name] * weights.get(name, 0)
            total_weight += weights.get(name, 0)

    if total_weight == 0:
        return 0.0
    return round(total / total_weight, 1)


def score_script(script_content: str, product_name: str,
                 llm_score_fn=None) -> Dict[str, Any]:
    """对剧本进行 6 维度评分。

    输入：
        script_content: 剧本内容
        product_name: 商品名称
        llm_score_fn: 可选的 LLM 评分函数，接收 (script_content, product_name) 返回维度分数
    输出：
        评分结果 dict，包含 overall_score, dimensions, feedback
    """
    if llm_score_fn:
        dimension_scores = llm_score_fn(script_content, product_name)
    else:
        # 默认示例分数，实际应由 LLM 生成
        dimension_scores = {
            "前3秒吸引力": 85,
            "故事新颖度": 78,
            "冲突与反转": 82,
            "商品自然植入": 88,
            "人物表现力": 75,
            "广告合规性": 90,
        }

    overall = compute_weighted_score(dimension_scores)

    dimensions = []
    for dim in SCORING_DIMENSIONS:
        dimensions.append({
            "name": dim["name"],
            "score": dimension_scores.get(dim["name"], 0),
            "weight": dim["weight"],
            "description": dim["description"],
        })

    # 生成反馈建议
    feedback_parts = []
    if dimension_scores.get("前3秒吸引力", 0) < 70:
        feedback_parts.append("前3秒钩子较弱，建议增强开头冲击力")
    if dimension_scores.get("故事新颖度", 0) < 70:
        feedback_parts.append("故事较为常见，建议寻找独特角度")
    if dimension_scores.get("冲突与反转", 0) < 70:
        feedback_parts.append("冲突不足，建议增加戏剧张力")
    if dimension_scores.get("商品自然植入", 0) < 70:
        feedback_parts.append("商品植入较生硬，建议更自然融入剧情")
    if dimension_scores.get("人物表现力", 0) < 70:
        feedback_parts.append("人物较为平面，建议丰富人设和台词")
    if dimension_scores.get("广告合规性", 0) < 70:
        feedback_parts.append("存在合规风险，建议修改后再发布")
    if not feedback_parts:
        feedback_parts.append("整体表现良好，可进入制作环节")

    return {
        "overall_score": overall,
        "dimensions": dimensions,
        "feedback": "；".join(feedback_parts),
    }


def filter_ideas_by_score(ideas: List[Dict[str, Any]],
                          scores: List[float],
                          min_score: float = 70.0,
                          top_n: Optional[int] = None) -> List[Tuple[Dict[str, Any], float]]:
    """根据评分筛选创意。

    输入：
        ideas: 创意列表
        scores: 对应评分列表
        min_score: 最低分数阈值
        top_n: 返回前 N 个，None 表示返回所有通过阈值的
    输出：
        (创意, 评分) 元组列表，按评分降序
    """
    scored = [(idea, score) for idea, score in zip(ideas, scores) if score >= min_score]
    scored.sort(key=lambda x: x[1], reverse=True)
    if top_n is not None:
        scored = scored[:top_n]
    return scored


def rank_ideas(ideas: List[Dict[str, Any]],
               scores: List[float]) -> List[Dict[str, Any]]:
    """对创意按评分排名，返回带排名的列表。

    输出：
        每个元素包含原创意字段及 score, rank 字段
    """
    scored = [(idea, score) for idea, score in zip(ideas, scores)]
    scored.sort(key=lambda x: x[1], reverse=True)
    ranked = []
    for rank, (idea, score) in enumerate(scored, start=1):
        item = dict(idea)
        item["score"] = score
        item["rank"] = rank
        ranked.append(item)
    return ranked
