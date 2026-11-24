"""AI Story Commerce — AI 编剧引擎测试套件"""

import sys
import os
import unittest
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "backend", "stdlib"))

from app.ai_engine import AIScriptEngine
from app.ai_engine.agents import (
    ProductResearchAgent,
    ConsumerPortraitAgent,
    CreativeDirectorAgent,
    ScreenwriterAgent,
    ComplianceReviewerAgent,
    ScriptScorer,
    select_best_ideas,
)
from app.ai_engine.scorer import (
    compute_weighted_score,
    score_script,
    filter_ideas_by_score,
    rank_ideas,
    SCORING_DIMENSIONS,
)
from app.ai_engine.prompts import PROMPT_TEMPLATES, STORY_TYPES


class ProductResearchAgentTest(unittest.TestCase):
    """测试商品研究员 Agent"""

    def test_analyze_returns_structured_report(self):
        agent = ProductResearchAgent()
        result = agent.analyze({
            "product_name": "测试洗衣液",
            "category": "home_cleaning",
            "price_cny": 39.9,
            "selling_points": "去污力强、香味持久",
            "target_audience": "年轻家庭",
            "usage_scenarios": "日常洗衣",
            "proof_materials": "第三方检测报告",
        })
        self.assertEqual(result["agent"], "product_researcher")
        self.assertIn("report", result)
        self.assertIn("consumer_profile", result["report"])
        self.assertIn("purchase_motivations", result["report"])
        self.assertIn("pain_points", result["report"])
        self.assertIn("ad_angles", result["report"])
        self.assertIsInstance(result["report"]["ad_angles"], list)


class ConsumerPortraitAgentTest(unittest.TestCase):
    """测试消费者画像 Agent"""

    def test_analyze_returns_portrait(self):
        agent = ConsumerPortraitAgent()
        result = agent.analyze("测试商品", {"consumer_profile": {}})
        self.assertEqual(result["agent"], "consumer_portrait")
        self.assertIn("portrait", result)
        self.assertIn("core_tags", result["portrait"])
        self.assertIn("decision_path", result["portrait"])


class CreativeDirectorAgentTest(unittest.TestCase):
    """测试创意总监 Agent"""

    def test_generate_ideas_returns_10_ideas(self):
        agent = CreativeDirectorAgent()
        result = agent.generate_ideas(
            product_name="测试商品",
            selling_points="卖点A、卖点B",
            target_audience="年轻人",
            consumer_portrait={"core_tags": ["标签1"]},
            ad_angles=["角度1", "角度2"],
        )
        self.assertEqual(result["agent"], "creative_director")
        self.assertEqual(len(result["ideas"]), 10)
        # 检查故事类型多样性
        story_types = {idea["story_type"] for idea in result["ideas"]}
        self.assertGreaterEqual(len(story_types), 3)


class ScreenwriterAgentTest(unittest.TestCase):
    """测试商业编剧 Agent"""

    def test_write_script_returns_complete_script(self):
        agent = ScreenwriterAgent()
        creative = {
            "title": "测试创意",
            "story_type": "反转型",
            "hook": "钩子内容",
            "conflict": "冲突内容",
            "twist": "反转内容",
            "product_integration": "商品植入",
            "character_setting": "主角：普通人",
        }
        result = agent.write_script(
            creative=creative,
            product_name="测试商品",
            selling_points="卖点A",
            character_setting="主角：普通人",
        )
        self.assertEqual(result["agent"], "screenwriter")
        self.assertIn("script", result)
        self.assertIn("title", result["script"])
        self.assertIn("storyboards", result["script"])
        self.assertGreaterEqual(len(result["script"]["storyboards"]), 7)


class ComplianceReviewerAgentTest(unittest.TestCase):
    """测试广告审核员 Agent"""

    def test_review_returns_compliance_result(self):
        agent = ComplianceReviewerAgent()
        result = agent.review(
            script_content="测试剧本内容",
            product_name="测试商品",
            product_claims="去污力强",
        )
        self.assertEqual(result["agent"], "compliance_reviewer")
        self.assertIn("review", result)
        self.assertIn("compliant", result["review"])
        self.assertIn("risk_level", result["review"])


class ScriptScorerTest(unittest.TestCase):
    """测试剧本评分 Agent"""

    def test_score_returns_weighted_result(self):
        agent = ScriptScorer()
        result = agent.score(
            script_content="测试剧本",
            product_name="测试商品",
        )
        self.assertEqual(result["agent"], "script_scorer")
        self.assertIn("scores", result)
        self.assertIn("overall_score", result["scores"])
        self.assertIn("dimensions", result["scores"])
        self.assertGreaterEqual(result["scores"]["overall_score"], 0)
        self.assertLessEqual(result["scores"]["overall_score"], 100)


class SelectBestIdeasTest(unittest.TestCase):
    """测试创意筛选函数"""

    def test_select_best_ideas_returns_top_n(self):
        ideas = [{"id": f"idea_{i}"} for i in range(5)]
        scores = [60.0, 90.0, 75.0, 85.0, 50.0]
        top = select_best_ideas(ideas, scores, top_n=3)
        self.assertEqual(len(top), 3)
        # 检查是按分数降序排列
        top_scores = [idea.get("score", 0) for idea in top] if top else []
        # select_best_ideas returns just ideas without scores, check order by matching
        self.assertEqual(top[0]["id"], "idea_1")  # score 90


class ComputeWeightedScoreTest(unittest.TestCase):
    """测试加权评分计算"""

    def test_compute_weighted_score(self):
        scores = {
            "前3秒吸引力": 80,
            "故事新颖度": 70,
            "冲突与反转": 90,
            "商品自然植入": 85,
            "人物表现力": 75,
            "广告合规性": 100,
        }
        result = compute_weighted_score(scores)
        # 80*0.2 + 70*0.2 + 90*0.2 + 85*0.2 + 75*0.1 + 100*0.1
        expected = 80*0.2 + 70*0.2 + 90*0.2 + 85*0.2 + 75*0.1 + 100*0.1
        self.assertAlmostEqual(result, expected, places=1)


class ScoreScriptTest(unittest.TestCase):
    """测试剧本评分"""

    def test_score_script_structure(self):
        result = score_script("测试剧本内容", "测试商品")
        self.assertIn("overall_score", result)
        self.assertIn("dimensions", result)
        self.assertIn("feedback", result)
        self.assertEqual(len(result["dimensions"]), 6)
        for dim in result["dimensions"]:
            self.assertIn("name", dim)
            self.assertIn("score", dim)
            self.assertIn("weight", dim)


class FilterIdeasByScoreTest(unittest.TestCase):
    """测试创意按分数筛选"""

    def test_filter_by_min_score(self):
        ideas = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
        scores = [80.0, 50.0, 90.0]
        filtered = filter_ideas_by_score(ideas, scores, min_score=70.0)
        self.assertEqual(len(filtered), 2)
        # 检查按分数降序
        self.assertEqual(filtered[0][0]["id"], "c")  # 90分


class RankIdeasTest(unittest.TestCase):
    """测试创意排名"""

    def test_rank_ideas_assigns_ranks(self):
        ideas = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
        scores = [50.0, 90.0, 70.0]
        ranked = rank_ideas(ideas, scores)
        self.assertEqual(ranked[0]["rank"], 1)
        self.assertEqual(ranked[0]["id"], "b")  # 最高分
        self.assertEqual(ranked[0]["score"], 90.0)
        self.assertEqual(ranked[2]["rank"], 3)
        self.assertEqual(ranked[2]["id"], "a")  # 最低分


class PromptTemplatesTest(unittest.TestCase):
    """测试 Prompt 模板"""

    def test_all_templates_exist(self):
        expected_agents = [
            "product_research", "consumer_portrait", "creative_director",
            "screenwriter", "compliance_reviewer", "script_scoring",
        ]
        for agent in expected_agents:
            self.assertIn(agent, PROMPT_TEMPLATES)
            self.assertIsInstance(PROMPT_TEMPLATES[agent], str)
            self.assertGreater(len(PROMPT_TEMPLATES[agent]), 100)

    def test_story_types_diversity(self):
        self.assertGreaterEqual(len(STORY_TYPES), 6)
        self.assertIn("误会型", STORY_TYPES)
        self.assertIn("反转型", STORY_TYPES)
        self.assertIn("逆袭型", STORY_TYPES)


class AIScriptEngineTest(unittest.TestCase):
    """测试 AI 编剧引擎主控制器"""

    def test_run_full_pipeline(self):
        engine = AIScriptEngine()
        result = engine.run_full_pipeline({
            "product_name": "测试洗衣液",
            "category": "home_cleaning",
            "price_cny": 39.9,
            "specifications": "3kg装",
            "selling_points": "去污力强、香味持久、温和不伤手",
            "target_audience": "年轻家庭、宝妈",
            "usage_scenarios": "日常洗衣、宝宝衣物",
            "proof_materials": "第三方检测报告、用户评价",
        })
        self.assertIn("pipeline_id", result)
        self.assertEqual(result["product_name"], "测试洗衣液")
        self.assertIn("steps", result)
        self.assertIn("product_research", result["steps"])
        self.assertIn("consumer_portrait", result["steps"])
        self.assertIn("creative_ideas", result["steps"])
        self.assertIn("top_ideas", result["steps"])
        self.assertIn("scripts", result["steps"])
        self.assertIn("summary", result)
        # 检查生成了10个创意
        self.assertEqual(result["steps"]["creative_ideas"]["agent"], "creative_director")
        self.assertEqual(len(result["steps"]["creative_ideas"]["ideas"]), 10)
        # 检查选出了3个top创意
        self.assertEqual(len(result["steps"]["top_ideas"]), 3)
        # 检查生成了剧本
        self.assertGreaterEqual(len(result["steps"]["scripts"]), 1)
        # 检查摘要
        self.assertEqual(result["summary"]["total_ideas_generated"], 10)
        self.assertEqual(result["summary"]["top_ideas_selected"], 3)


if __name__ == "__main__":
    unittest.main()
