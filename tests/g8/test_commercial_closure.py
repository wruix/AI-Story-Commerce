"""AI Story Commerce — G8 商业闭环验证测试套件

对应立项方案 D22–D30 阶段：商业订单与闭环验收
"""

import sys
import os
import unittest
import json
import tempfile

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "backend", "stdlib"))

from app.db.session import get_db, init_db
import app.crud.crud as crud
from app.commercial_closure import (
    RequirementAnalysis,
    ProductionOrder,
    DeliveryAcceptance,
    AdPerformanceTracking,
    RetrospectiveAnalysis,
    InvestmentDecision,
    now_iso,
)


def _create_customer_and_project(conn):
    """创建客户和项目，返回 (customer, project)"""
    customer = crud.customer_create(conn, {
        "name": "测试商家",
        "contact_person": "张三",
        "phone": "13800000000",
    })
    project = crud.project_create(conn, {
        "name": "测试商业项目",
        "customer_id": customer["id"],
        "budget_cny": 10000.0,
    })
    return customer, project


def _create_ad_with_performance(conn, project_id, title="测试广告"):
    """创建带效果数据的广告，返回 (ad, record)"""
    ad = crud.advertisement_create(conn, {
        "project_id": project_id,
        "version": 1,
        "title": title,
        "status": "reviewed",
    })
    record = crud.publishing_record_create(conn, {
        "advertisement_id": ad["id"],
        "platform": "douyin",
        "account_name": "测试账号",
        "ai_disclosure_posted": True,
    })
    crud.performance_metric_create(conn, {
        "publishing_record_id": record["id"],
        "views": 5000,
        "completion_rate": 0.65,
        "likes": 300,
        "comments": 30,
        "shares": 20,
        "product_clicks": 100,
        "orders": 3,
        "cost_cny": 300.0,
    })
    return ad, record


class RequirementAnalysisTest(unittest.TestCase):
    """测试商家需求分析"""

    def setUp(self):
        self._db_fd, self._db_path = tempfile.mkstemp(suffix=".db")
        import app.db.session as session
        import pathlib
        self._orig_db_path = session.DATABASE_PATH
        session.DATABASE_PATH = pathlib.Path(self._db_path)
        init_db()

    def tearDown(self):
        import app.db.session as session
        session.DATABASE_PATH = self._orig_db_path
        os.close(self._db_fd)
        os.unlink(self._db_path)

    def test_create_requirement(self):
        with get_db() as conn:
            mgr = RequirementAnalysis()
            customer, project = _create_customer_and_project(conn)

            req = mgr.create_requirement(
                conn, customer["id"], project["id"],
                product_name="测试洗衣液",
                budget_cny=5000.0,
                target_audience="年轻家庭",
                preferred_story_type="反转型",
                compliance_boundary="不夸大功效",
            )
            self.assertIsNotNone(req)
            self.assertEqual(req["customer_id"], customer["id"])
            self.assertEqual(req["status"], "pending")

    def test_list_requirements(self):
        with get_db() as conn:
            mgr = RequirementAnalysis()
            customer, project = _create_customer_and_project(conn)

            mgr.create_requirement(conn, customer["id"], project["id"], product_name="商品A")
            mgr.create_requirement(conn, customer["id"], project["id"], product_name="商品B")

            reqs = mgr.list_requirements(conn, customer_id=customer["id"])
            self.assertEqual(len(reqs), 2)

    def test_update_requirement_status(self):
        with get_db() as conn:
            mgr = RequirementAnalysis()
            customer, project = _create_customer_and_project(conn)

            req = mgr.create_requirement(conn, customer["id"], project["id"])
            resource_id = req["resource_id"]

            updated = mgr.update_requirement_status(conn, resource_id, "accepted")
            self.assertEqual(updated["status"], "accepted")


class ProductionOrderTest(unittest.TestCase):
    """测试生产订单管理"""

    def setUp(self):
        self._db_fd, self._db_path = tempfile.mkstemp(suffix=".db")
        import app.db.session as session
        import pathlib
        self._orig_db_path = session.DATABASE_PATH
        session.DATABASE_PATH = pathlib.Path(self._db_path)
        init_db()

    def tearDown(self):
        import app.db.session as session
        session.DATABASE_PATH = self._orig_db_path
        os.close(self._db_fd)
        os.unlink(self._db_path)

    def test_create_and_update_order(self):
        with get_db() as conn:
            mgr = ProductionOrder()
            req_mgr = RequirementAnalysis()
            customer, project = _create_customer_and_project(conn)

            req = req_mgr.create_requirement(conn, customer["id"], project["id"])
            order = mgr.create_order(
                conn, customer["id"], req["resource_id"],
                ad_title="定制广告 v1",
                agreed_price_cny=5000.0,
            )
            self.assertIsNotNone(order)
            self.assertEqual(order["status"], "pending")

            # 更新订单状态
            updated = mgr.update_order_status(conn, order["resource_id"], "in_production")
            self.assertEqual(updated["status"], "in_production")

    def test_list_orders(self):
        with get_db() as conn:
            mgr = ProductionOrder()
            req_mgr = RequirementAnalysis()
            customer, project = _create_customer_and_project(conn)

            req = req_mgr.create_requirement(conn, customer["id"], project["id"])
            mgr.create_order(conn, customer["id"], req["resource_id"], "广告1")
            mgr.create_order(conn, customer["id"], req["resource_id"], "广告2")

            orders = mgr.list_orders(conn, customer_id=customer["id"])
            self.assertEqual(len(orders), 2)


class DeliveryAcceptanceTest(unittest.TestCase):
    """测试客户交付与验收"""

    def setUp(self):
        self._db_fd, self._db_path = tempfile.mkstemp(suffix=".db")
        import app.db.session as session
        import pathlib
        self._orig_db_path = session.DATABASE_PATH
        session.DATABASE_PATH = pathlib.Path(self._db_path)
        init_db()

    def tearDown(self):
        import app.db.session as session
        session.DATABASE_PATH = self._orig_db_path
        os.close(self._db_fd)
        os.unlink(self._db_path)

    def test_delivery_and_acceptance(self):
        with get_db() as conn:
            dlv_mgr = DeliveryAcceptance()
            ord_mgr = ProductionOrder()
            req_mgr = RequirementAnalysis()
            customer, project = _create_customer_and_project(conn)

            req = req_mgr.create_requirement(conn, customer["id"], project["id"])
            order = ord_mgr.create_order(conn, customer["id"], req["resource_id"], "定制广告")

            # 交付
            delivery = dlv_mgr.record_delivery(
                conn, order["resource_id"],
                ad_file_path="/data/outputs/final_ad.mp4",
                ad_sha256="abc123def456",
            )
            self.assertEqual(delivery["acceptance_status"], "pending")

            # 验收通过
            result = dlv_mgr.record_acceptance(
                conn, delivery["resource_id"],
                accepted=True,
                acceptance_notes="广告质量符合要求",
            )
            self.assertEqual(result["acceptance_status"], "accepted")

    def test_delivery_rejection(self):
        with get_db() as conn:
            dlv_mgr = DeliveryAcceptance()
            ord_mgr = ProductionOrder()
            req_mgr = RequirementAnalysis()
            customer, project = _create_customer_and_project(conn)

            req = req_mgr.create_requirement(conn, customer["id"], project["id"])
            order = ord_mgr.create_order(conn, customer["id"], req["resource_id"], "定制广告")

            delivery = dlv_mgr.record_delivery(
                conn, order["resource_id"],
                ad_file_path="/data/outputs/final_ad.mp4",
                ad_sha256="abc123def456",
            )

            # 验收拒绝
            result = dlv_mgr.record_acceptance(
                conn, delivery["resource_id"],
                accepted=False,
                acceptance_notes="人物表现不符合预期",
                revision_request="重新制作前3秒钩子",
            )
            self.assertEqual(result["acceptance_status"], "rejected")
            self.assertEqual(result["revision_count"], 1)

    def test_list_deliveries(self):
        with get_db() as conn:
            dlv_mgr = DeliveryAcceptance()
            ord_mgr = ProductionOrder()
            req_mgr = RequirementAnalysis()
            customer, project = _create_customer_and_project(conn)

            req = req_mgr.create_requirement(conn, customer["id"], project["id"])
            order = ord_mgr.create_order(conn, customer["id"], req["resource_id"], "广告")

            dlv_mgr.record_delivery(conn, order["resource_id"], "/path/a.mp4", "sha1")
            dlv_mgr.record_delivery(conn, order["resource_id"], "/path/b.mp4", "sha2")

            deliveries = dlv_mgr.list_deliveries(conn, order_resource_id=order["resource_id"])
            self.assertEqual(len(deliveries), 2)


class AdPerformanceTrackingTest(unittest.TestCase):
    """测试广告数据追踪"""

    def setUp(self):
        self._db_fd, self._db_path = tempfile.mkstemp(suffix=".db")
        import app.db.session as session
        import pathlib
        self._orig_db_path = session.DATABASE_PATH
        session.DATABASE_PATH = pathlib.Path(self._db_path)
        init_db()

    def tearDown(self):
        import app.db.session as session
        session.DATABASE_PATH = self._orig_db_path
        os.close(self._db_fd)
        os.unlink(self._db_path)

    def test_record_and_summary(self):
        with get_db() as conn:
            tracker = AdPerformanceTracking()
            project = crud.project_create(conn, {"name": "测试项目"})
            ad, record = _create_ad_with_performance(conn, project["id"])

            # 再录入一条数据
            tracker.record_customer_ad_performance(
                conn, record["id"],
                views=3000, orders=2, cost_cny=200.0,
            )

            summary = tracker.get_customer_ad_summary(conn, ad["id"])
            self.assertEqual(summary["advertisement_id"], ad["id"])
            self.assertEqual(summary["total_views"], 8000)  # 5000 + 3000
            self.assertEqual(summary["total_orders"], 5)    # 3 + 2
            self.assertEqual(summary["data_points"], 2)


class RetrospectiveAnalysisTest(unittest.TestCase):
    """测试复盘分析"""

    def setUp(self):
        self._db_fd, self._db_path = tempfile.mkstemp(suffix=".db")
        import app.db.session as session
        import pathlib
        self._orig_db_path = session.DATABASE_PATH
        session.DATABASE_PATH = pathlib.Path(self._db_path)
        init_db()

    def tearDown(self):
        import app.db.session as session
        session.DATABASE_PATH = self._orig_db_path
        os.close(self._db_fd)
        os.unlink(self._db_path)

    def test_analyze_story_type_performance(self):
        with get_db() as conn:
            mgr = RetrospectiveAnalysis()
            project = crud.project_create(conn, {"name": "测试项目"})

            # 创建两个不同类型的广告
            product = crud.product_create(conn, {
                "project_id": project["id"],
                "name": "商品",
                "category": "other",
            })

            idea1 = crud.story_idea_create(conn, {
                "product_id": product["id"],
                "title": "误会型创意",
                "story_type": "误会型",
            })
            script1 = crud.script_create(conn, {
                "story_idea_id": idea1["id"],
                "version": 1,
                "title": "脚本1",
                "content": "内容1",
            })
            ad1 = crud.advertisement_create(conn, {
                "project_id": project["id"],
                "script_id": script1["id"],
                "version": 1,
                "title": "误会型广告",
                "status": "reviewed",
            })
            rec1 = crud.publishing_record_create(conn, {
                "advertisement_id": ad1["id"],
                "platform": "douyin",
            })
            crud.performance_metric_create(conn, {
                "publishing_record_id": rec1["id"],
                "views": 5000,
                "orders": 3,
                "cost_cny": 300.0,
            })

            idea2 = crud.story_idea_create(conn, {
                "product_id": product["id"],
                "title": "反转型创意",
                "story_type": "反转型",
            })
            script2 = crud.script_create(conn, {
                "story_idea_id": idea2["id"],
                "version": 1,
                "title": "脚本2",
                "content": "内容2",
            })
            ad2 = crud.advertisement_create(conn, {
                "project_id": project["id"],
                "script_id": script2["id"],
                "version": 1,
                "title": "反转型广告",
                "status": "reviewed",
            })
            rec2 = crud.publishing_record_create(conn, {
                "advertisement_id": ad2["id"],
                "platform": "douyin",
            })
            crud.performance_metric_create(conn, {
                "publishing_record_id": rec2["id"],
                "views": 8000,
                "orders": 10,
                "cost_cny": 500.0,
            })

            result = mgr.analyze_story_type_performance(conn)
            self.assertIn("误会型", result["story_type_summary"])
            self.assertIn("反转型", result["story_type_summary"])
            self.assertEqual(result["best_story_type"], "反转型")


class InvestmentDecisionTest(unittest.TestCase):
    """测试投资决策支持"""

    def setUp(self):
        self._db_fd, self._db_path = tempfile.mkstemp(suffix=".db")
        import app.db.session as session
        import pathlib
        self._orig_db_path = session.DATABASE_PATH
        session.DATABASE_PATH = pathlib.Path(self._db_path)
        init_db()

    def tearDown(self):
        import app.db.session as session
        session.DATABASE_PATH = self._orig_db_path
        os.close(self._db_fd)
        os.unlink(self._db_path)

    def test_decision_continue_expand(self):
        with get_db() as conn:
            mgr = InvestmentDecision()
            commercial = {"paid_trial_orders": 1, "customer_count": 5}
            content = {"total_ads": 9}

            result = mgr.evaluate_30_day_result(conn, commercial, content)
            self.assertEqual(result["decision"]["branch"], "continue_expand")
            self.assertEqual(result["decision"]["action"], "继续扩大服务")
            self.assertTrue(result["decision"]["branch"] == "continue_expand")

    def test_decision_adjust_business(self):
        with get_db() as conn:
            mgr = InvestmentDecision()
            commercial = {"paid_trial_orders": 0, "customer_count": 5}
            content = {"total_ads": 9}

            result = mgr.evaluate_30_day_result(conn, commercial, content)
            self.assertEqual(result["decision"]["branch"], "adjust_business")
            self.assertEqual(result["decision"]["action"], "调整商业方案")
            self.assertEqual(result["decision"]["branch"], "adjust_business")

    def test_decision_pause_expand(self):
        with get_db() as conn:
            mgr = InvestmentDecision()
            commercial = {"paid_trial_orders": 0, "customer_count": 0}
            content = {"total_ads": 0}

            result = mgr.evaluate_30_day_result(conn, commercial, content)
            self.assertEqual(result["decision"]["branch"], "pause_expand")
            self.assertEqual(result["decision"]["action"], "暂停扩张")
            self.assertEqual(result["decision"]["branch"], "pause_expand")

    def test_generate_investment_report(self):
        with get_db() as conn:
            mgr = InvestmentDecision()
            g7_report = {
                "commercial_metrics": {"paid_trial_orders": 1, "customer_count": 3},
                "content_metrics": {"total_ads": 9, "total_scripts": 9, "total_creative_ideas": 30},
            }
            report = mgr.generate_investment_report(conn, g7_report)
            self.assertEqual(report["report_type"], "30_day_investment_decision")
            self.assertTrue(report["next_stage_authorization"])


if __name__ == "__main__":
    unittest.main()
