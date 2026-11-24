"""AI Story Commerce — AI 编剧引擎主控制器

编排五个 Agent 的协作流程：
商品研究员 → 消费者画像 → 创意总监 → 商业编剧 → 广告审核员 → 评分筛选

输入：商品资料
输出：10 个剧情创意、筛选结果、完整剧本
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.ai_engine.agents import (
    ProductResearchAgent,
    ConsumerPortraitAgent,
    CreativeDirectorAgent,
    ScreenwriterAgent,
    ComplianceReviewerAgent,
    ScriptScorer,
    select_best_ideas,
)
from app.ai_engine.scorer import score_script, filter_ideas_by_score, rank_ideas


def now_iso():
    return datetime.now(timezone.utc).isoformat()


class AIScriptEngine:
    """AI 编剧引擎主控制器"""

    def __init__(self):
        self.product_researcher = ProductResearchAgent()
        self.consumer_portrait = ConsumerPortraitAgent()
        self.creative_director = CreativeDirectorAgent()
        self.screenwriter = ScreenwriterAgent()
        self.compliance_reviewer = ComplianceReviewerAgent()
        self.scorer = ScriptScorer()

    def run_full_pipeline(self, product_data: Dict[str, Any],
                          llm_inference_fn=None) -> Dict[str, Any]:
        """运行完整的 AI 编剧流水线。

        输入：
            product_data: 商品资料，包含 product_name, category, price_cny,
                         specifications, selling_points, target_audience,
                         usage_scenarios, proof_materials
            llm_inference_fn: 可选的 LLM 推理函数，接收 prompt 返回生成文本
        输出：
            完整流水线结果，包含所有中间产出和最终剧本
        """
        product_name = product_data.get("product_name", "未知商品")
        pipeline_id = str(uuid.uuid4())
        started_at = now_iso()

        # 步骤 1: 商品研究
        research_result = self.product_researcher.analyze(product_data)

        # 步骤 2: 消费者画像
        portrait_result = self.consumer_portrait.analyze(
            product_name, research_result["report"]
        )

        # 步骤 3: 剧情创意（10 个）
        ad_angles = research_result["report"].get("ad_angles", [])
        ideas_result = self.creative_director.generate_ideas(
            product_name=product_name,
            selling_points=product_data.get("selling_points", ""),
            target_audience=product_data.get("target_audience", ""),
            consumer_portrait=portrait_result["portrait"],
            ad_angles=ad_angles,
        )

        # 步骤 4: 为每个创意评分（模拟）
        idea_scores = []
        for idea in ideas_result["ideas"]:
            score_result = score_script(
                script_content=idea.get("hook", "") + " " + idea.get("conflict", ""),
                product_name=product_name,
            )
            idea_scores.append(score_result["overall_score"])

        # 步骤 5: 筛选前 3 个创意
        top_ideas = select_best_ideas(
            ideas_result["ideas"], idea_scores, top_n=3
        )

        # 步骤 6: 为每个选中创意生成完整剧本
        scripts = []
        for idea in top_ideas:
            script_result = self.screenwriter.write_script(
                creative=idea,
                product_name=product_name,
                selling_points=product_data.get("selling_points", ""),
                character_setting=idea.get("character_setting", ""),
            )
            scripts.append(script_result)

        # 步骤 7: 合规审核（对每个剧本）
        reviewed_scripts = []
        for script_result in scripts:
            script_content = script_result["script"].get("full_dialogue", "")
            review_result = self.compliance_reviewer.review(
                script_content=script_content,
                product_name=product_name,
                product_claims=product_data.get("selling_points", ""),
            )
            reviewed_scripts.append({
                "script": script_result,
                "compliance_review": review_result,
            })

        # 步骤 8: 剧本评分筛选
        scored_scripts = []
        for item in reviewed_scripts:
            script_content = item["script"]["script"].get("full_dialogue", "")
            score_result = score_script(
                script_content=script_content,
                product_name=product_name,
            )
            scored_scripts.append({
                "script": item["script"],
                "compliance_review": item["compliance_review"],
                "score": score_result,
            })

        # 按总分排序
        scored_scripts.sort(
            key=lambda x: x["score"]["overall_score"],
            reverse=True,
        )

        completed_at = now_iso()

        return {
            "pipeline_id": pipeline_id,
            "product_name": product_name,
            "started_at": started_at,
            "completed_at": completed_at,
            "steps": {
                "product_research": research_result,
                "consumer_portrait": portrait_result,
                "creative_ideas": ideas_result,
                "top_ideas": top_ideas,
                "scripts": scored_scripts,
            },
            "summary": {
                "total_ideas_generated": len(ideas_result["ideas"]),
                "top_ideas_selected": len(top_ideas),
                "scripts_generated": len(scored_scripts),
                "best_script_score": scored_scripts[0]["score"]["overall_score"] if scored_scripts else 0,
                "all_compliant": all(
                    s["compliance_review"]["review"]["compliant"]
                    for s in scored_scripts
                ),
            },
        }


__all__ = ["AIScriptEngine"]
