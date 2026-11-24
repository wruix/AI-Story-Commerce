"""AI Story Commerce — AI 编剧引擎 Agent 模块

实现五个专门角色的 Agent：
1. 商品研究员 - 商品分析
2. 创意总监 - 剧情创意
3. 商业编剧 - 剧本生成
4. 广告审核员 - 合规检查
5. 评分筛选机制 - 剧本评分

每个 Agent 接收结构化输入，返回结构化 JSON 输出。
"""

import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.ai_engine.prompts import (
    PRODUCT_RESEARCH_PROMPT,
    CONSUMER_PORTRAIT_PROMPT,
    CREATIVE_DIRECTOR_PROMPT,
    SCREENWRITER_PROMPT,
    COMPLIANCE_REVIEWER_PROMPT,
    SCRIPT_SCORING_PROMPT,
    SCORING_DIMENSIONS,
    STORY_TYPES,
)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def _extract_json(text: str) -> Any:
    """从文本中提取 JSON 对象，容错处理。"""
    text = text.strip()
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 尝试提取 ```json ... ``` 块
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    # 尝试提取第一个 { ... } 块
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    raise ValueError(f"无法从文本中提取有效 JSON: {text[:200]}...")


class ProductResearchAgent:
    """商品研究员 Agent - 理解商品与消费者"""

    def analyze(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析商品，生成商品研究报告。

        输入：
            product_data: 包含 product_name, category, price_cny, specifications,
                         selling_points, target_audience, usage_scenarios, proof_materials
        输出：
            商品研究报告（dict）
        """
        prompt = PRODUCT_RESEARCH_PROMPT.format(
            product_name=product_data.get("product_name", ""),
            category=product_data.get("category", ""),
            price_cny=product_data.get("price_cny", ""),
            specifications=product_data.get("specifications", ""),
            selling_points=product_data.get("selling_points", ""),
            target_audience=product_data.get("target_audience", ""),
            usage_scenarios=product_data.get("usage_scenarios", ""),
            proof_materials=product_data.get("proof_materials", ""),
        )

        # 在实际部署中，这里会调用 LLM API。当前为标准库实现，
        # 返回结构化模板，供后续接入真实模型。
        result = {
            "agent": "product_researcher",
            "prompt": prompt,
            "raw_input": product_data,
            "raw_output": None,  # 待 LLM 填充
            "report": {
                "consumer_profile": {
                    "age_range": "25-45",
                    "gender": "不限",
                    "occupation": "白领/自由职业者",
                    "consumption_habit": "注重性价比，偏好便捷购买",
                },
                "purchase_motivations": [
                    "解决具体生活痛点",
                    "提升生活质量",
                    "性价比高",
                ],
                "pain_points": [
                    "现有方案使用不便",
                    "效果不明显",
                    "价格过高",
                ],
                "usage_scenarios": product_data.get("usage_scenarios", "日常生活场景"),
                "competitor_analysis": {
                    "main_competitors": "市场同类产品",
                    "differentiation": "通过剧情广告突出独特卖点",
                },
                "ad_angles": product_data.get("selling_points", "").split("、")[:3],
            },
            "generated_at": now_iso(),
        }
        return result


class ConsumerPortraitAgent:
    """消费者画像 Agent"""

    def analyze(self, product_name: str, product_research: Dict[str, Any]) -> Dict[str, Any]:
        prompt = CONSUMER_PORTRAIT_PROMPT.format(
            product_name=product_name,
            product_research=json.dumps(product_research, ensure_ascii=False, indent=2),
        )
        result = {
            "agent": "consumer_portrait",
            "prompt": prompt,
            "raw_input": {"product_name": product_name, "product_research": product_research},
            "raw_output": None,
            "portrait": {
                "core_tags": ["注重生活品质", "抖音活跃用户", "追求性价比"],
                "daily_behavior": "刷短视频、网购、关注生活技巧",
                "media_habits": "抖音深夜时段活跃，偏好轻松幽默内容",
                "decision_path": "看到广告 → 产生兴趣 → 查看评价 → 下单",
                "price_sensitivity": "中等",
                "trusted_sources": "KOL推荐、真实用户评价",
            },
            "generated_at": now_iso(),
        }
        return result


class CreativeDirectorAgent:
    """创意总监 Agent - 设计故事与反转"""

    def generate_ideas(self, product_name: str, selling_points: str,
                       target_audience: str, consumer_portrait: Dict[str, Any],
                       ad_angles: List[str]) -> Dict[str, Any]:
        prompt = CREATIVE_DIRECTOR_PROMPT.format(
            product_name=product_name,
            selling_points=selling_points,
            target_audience=target_audience,
            consumer_portrait=json.dumps(consumer_portrait, ensure_ascii=False, indent=2),
            ad_angles="、".join(ad_angles),
        )

        # 生成 10 个不同类型的创意
        ideas = []
        for i in range(10):
            story_type = STORY_TYPES[i % len(STORY_TYPES)]
            ideas.append({
                "id": f"idea_{i+1}",
                "title": f"{product_name}·{story_type}创意{i+1}",
                "story_type": story_type,
                "hook": f"前3秒：{product_name}相关的钩子{i+1}",
                "conflict": f"第3-7秒：冲突情节{i+1}",
                "twist": f"第7-11秒：升级或反转{i+1}",
                "product_integration": f"第11-15秒：{product_name}自然植入",
                "character_setting": "主角：普通消费者，配角：朋友/家人",
                "emotional_resonance": "生活共鸣",
            })

        result = {
            "agent": "creative_director",
            "prompt": prompt,
            "raw_input": {
                "product_name": product_name,
                "selling_points": selling_points,
                "target_audience": target_audience,
                "consumer_portrait": consumer_portrait,
                "ad_angles": ad_angles,
            },
            "raw_output": None,
            "ideas": ideas,
            "generated_at": now_iso(),
        }
        return result


class ScreenwriterAgent:
    """商业编剧 Agent - 编写完整剧本"""

    def write_script(self, creative: Dict[str, Any], product_name: str,
                     selling_points: str, character_setting: str) -> Dict[str, Any]:
        prompt = SCREENWRITER_PROMPT.format(
            creative_title=creative.get("title", ""),
            story_type=creative.get("story_type", ""),
            product_name=product_name,
            selling_points=selling_points,
            character_setting=character_setting,
            hook=creative.get("hook", ""),
            conflict=creative.get("conflict", ""),
            twist=creative.get("twist", ""),
            product_integration=creative.get("product_integration", ""),
            purchase_reason=creative.get("product_integration", ""),
        )

        # 生成 7-10 个镜头的分镜表
        storyboards = []
        for i in range(1, 8):
            storyboards.append({
                "shot_number": i,
                "description": f"第{i}镜头：{creative.get('hook', '') if i == 1 else '剧情发展'}",
                "image_prompt": f"镜头{i}画面提示词：{product_name}相关场景",
                "dialogue": f"第{i}镜头对白",
                "sound_effect": f"第{i}镜头音效",
                "duration_seconds": 2.0 if i < 7 else 1.0,
            })

        result = {
            "agent": "screenwriter",
            "prompt": prompt,
            "raw_input": {
                "creative": creative,
                "product_name": product_name,
                "selling_points": selling_points,
                "character_setting": character_setting,
            },
            "raw_output": None,
            "script": {
                "title": creative.get("title", ""),
                "characters": [
                    {"name": "主角", "personality": "普通消费者", "dialogue_style": "自然口语"},
                    {"name": "配角", "personality": "朋友/家人", "dialogue_style": "自然口语"},
                ],
                "storyboards": storyboards,
                "full_dialogue": "完整对白内容",
                "product_placement": f"第11-15秒：{product_name}展示与购买理由",
                "time_allocation": {
                    "0-3s": "钩子",
                    "3-7s": "冲突",
                    "7-11s": "升级/反转",
                    "11-15s": "商品与购买理由",
                },
            },
            "generated_at": now_iso(),
        }
        return result


class ComplianceReviewerAgent:
    """广告审核员 Agent - 真实性和合规检查"""

    def review(self, script_content: str, product_name: str,
               product_claims: str) -> Dict[str, Any]:
        prompt = COMPLIANCE_REVIEWER_PROMPT.format(
            script_content=script_content,
            product_name=product_name,
            product_claims=product_claims,
        )

        result = {
            "agent": "compliance_reviewer",
            "prompt": prompt,
            "raw_input": {
                "script_content": script_content,
                "product_name": product_name,
                "product_claims": product_claims,
            },
            "raw_output": None,
            "review": {
                "compliant": True,
                "issues": [],
                "suggestions": "建议在发布时标注 AI 生成内容",
                "risk_level": "低",
                "checks": {
                    "product_authenticity": True,
                    "fictional_experience_check": True,
                    "extreme_language": False,
                    "medical_health_risk": False,
                    "ai_disclosure_needed": True,
                    "portrait_authorization": True,
                    "music_license": True,
                    "trademark_check": True,
                },
            },
            "generated_at": now_iso(),
        }
        return result


class ScriptScorer:
    """剧本评分与筛选机制"""

    def score(self, script_content: str, product_name: str) -> Dict[str, Any]:
        prompt = SCRIPT_SCORING_PROMPT.format(
            script_content=script_content,
            product_name=product_name,
        )

        # 计算加权总分（示例分数，实际应由 LLM 给出）
        dimension_scores = {
            "前3秒吸引力": 85,
            "故事新颖度": 78,
            "冲突与反转": 82,
            "商品自然植入": 88,
            "人物表现力": 75,
            "广告合规性": 90,
        }
        weights = {d["name"]: d["weight"] for d in SCORING_DIMENSIONS}
        overall = sum(dimension_scores[d["name"]] * weights[d["name"]] for d in SCORING_DIMENSIONS)

        result = {
            "agent": "script_scorer",
            "prompt": prompt,
            "raw_input": {"script_content": script_content, "product_name": product_name},
            "raw_output": None,
            "scores": {
                "overall_score": round(overall, 1),
                "dimensions": [
                    {"name": d["name"], "score": dimension_scores[d["name"]], "weight": d["weight"]}
                    for d in SCORING_DIMENSIONS
                ],
                "feedback": "整体表现良好，建议优化前3秒钩子，增强商品植入自然度",
            },
            "generated_at": now_iso(),
        }
        return result


def select_best_ideas(ideas: List[Dict[str, Any]], scores: List[float],
                      top_n: int = 3) -> List[Dict[str, Any]]:
    """根据评分筛选最佳创意。

    输入：
        ideas: 创意列表
        scores: 对应的评分列表
        top_n: 返回前 N 个
    输出：
        排序后的前 N 个创意
    """
    scored = list(zip(ideas, scores))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [idea for idea, _ in scored[:top_n]]
