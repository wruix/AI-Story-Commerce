"""AI Story Commerce — G7 数据分析与独立验收测试套件"""

import sys
import os
import unittest
import json
import tempfile

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "backend", "stdlib"))

from app.db.session import get_db, init_db
import app.crud.crud as crud
from app.data_analysis import (
    PerformanceDataManager,
    MetricsCalculator,
    CreativeEffectComparator,
    ProjectOperationsReport,
    now_iso,
)


def _create_full_chain(conn):
    """创建项目-商品-创意-剧本-分镜-广告-发布记录的完整链条"""
    project = crud.project_create(conn, {"name": "测试项目", "budget_cny": 10000.0})
    customer = crud.customer_create(conn, {"name": "测试商家", "contact_person": "张三"})
    crud.project_update(conn, project["id"], {"customer_id": customer["id"]})
    product = crud.product_create(conn, {
        "project_id": project["id"],
        "name": "测试商品",
        "category": "home_cleaning",
        "price_cny": 99.0,
    })
    idea = crud.story_idea_create(conn, {
        "product_id": product["id"],
        "title": "测试创意",
        "story_type": "反转型",
    })
    script = crud.script_create(conn, {
        "story_idea_id": idea["id"],
        "version": 1,
        "title": "测试剧本",
        "content": "剧本内容",
    })
    ad = crud.advertisement_create(conn, {
        "project_id": project["id"],
        "script_id": script["id"],
        "version": 1,
        "title": "测试广告",
        "status": "reviewed",
    })
    record = crud.publishing_record_create(conn, {
        "advertisement_id": ad["id"],
        "platform": "douyin",
        "account_name": "测试账号",
        "ai_disclosure_posted": True,
    })
    return project, customer, product, idea, script, ad, record


class PerformanceDataManagerTest(unittest.TestCase):
    """测试广告效果数据录入"""

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

    def test_record_performance(self):
        with get_db() as conn:
            mgr = PerformanceDataManager()
            _, _, _, _, _, ad, record = _create_full_chain(conn)

            metric = mgr.record_performance(
                conn, record["id"],
                views=10000,
                completion_rate=0.65,
                likes=500,
                comments=50,
                shares=30,
                product_clicks=200,
                orders=5,
                cost_cny=500.0,
            )
            self.assertIsNotNone(metric["id"])
            self.assertEqual(metric["views"], 10000)
            self.assertEqual(metric["completion_rate"], 0.65)
            self.assertEqual(metric["likes"], 500)
            self.assertEqual(metric["cpa_cny"], 100.0)  # 500/5 = 100

    def test_list_metrics(self):
        with get_db() as conn:
            mgr = PerformanceDataManager()
            _, _, _, _, _, ad, record = _create_full_chain(conn)

            mgr.record_performance(conn, record["id"], views=1000, cost_cny=100.0)
            mgr.record_performance(conn, record["id"], views=2000, cost_cny=200.0)

            metrics = mgr.list_metrics(conn, record["id"])
            self.assertEqual(len(metrics), 2)

    def test_get_latest_metric(self):
        with get_db() as conn:
            mgr = PerformanceDataManager()
            _, _, _, _, _, ad, record = _create_full_chain(conn)

            m1 = mgr.record_performance(conn, record["id"], views=1000, recorded_at="2026-11-23T10:00:00.000000+00:00")
            m2 = mgr.record_performance(conn, record["id"], views=2000, recorded_at="2026-11-23T10:00:00.000001+00:00")

            latest = mgr.get_latest_metric(conn, record["id"])
            self.assertEqual(latest["id"], m2["id"])
            self.assertEqual(latest["views"], 2000)


class MetricsCalculatorTest(unittest.TestCase):
    """测试指标计算器"""

    def test_calculate_ctr(self):
        result = MetricsCalculator.calculate_ctr(1000, 50)
        self.assertEqual(result, 0.05)

        result = MetricsCalculator.calculate_ctr(0, 50)
        self.assertIsNone(result)

    def test_calculate_cvr(self):
        result = MetricsCalculator.calculate_cvr(100, 10)
        self.assertEqual(result, 0.1)

        result = MetricsCalculator.calculate_cvr(0, 10)
        self.assertIsNone(result)

    def test_calculate_cpa(self):
        result = MetricsCalculator.calculate_cpa(500.0, 5)
        self.assertEqual(result, 100.0)

        result = MetricsCalculator.calculate_cpa(500.0, 0)
        self.assertIsNone(result)

    def test_calculate_roas(self):
        result = MetricsCalculator.calculate_roas(2000.0, 500.0)
        self.assertEqual(result, 4.0)

        result = MetricsCalculator.calculate_roas(2000.0, 0)
        self.assertIsNone(result)

    def test_calculate_completion_rate(self):
        result = MetricsCalculator.calculate_completion_rate(1000, 650)
        self.assertEqual(result, 0.65)


class CreativeEffectComparatorTest(unittest.TestCase):
    """测试创意效果比较"""

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

    def test_compare_advertisements(self):
        with get_db() as conn:
            comparator = CreativeEffectComparator()
            project = crud.project_create(conn, {"name": "测试项目"})

            # 创建两个广告
            ad1 = crud.advertisement_create(conn, {
                "project_id": project["id"],
                "version": 1,
                "title": "广告A",
                "status": "reviewed",
            })
            ad2 = crud.advertisement_create(conn, {
                "project_id": project["id"],
                "version": 2,
                "title": "广告B",
                "status": "reviewed",
            })

            # 为两个广告创建发布记录和效果数据
            rec1 = crud.publishing_record_create(conn, {
                "advertisement_id": ad1["id"],
                "platform": "douyin",
            })
            rec2 = crud.publishing_record_create(conn, {
                "advertisement_id": ad2["id"],
                "platform": "douyin",
            })

            crud.performance_metric_create(conn, {
                "publishing_record_id": rec1["id"],
                "views": 5000,
                "product_clicks": 100,
                "orders": 3,
                "cost_cny": 300.0,
            })
            crud.performance_metric_create(conn, {
                "publishing_record_id": rec2["id"],
                "views": 8000,
                "product_clicks": 200,
                "orders": 10,
                "cost_cny": 500.0,
            })

            result = comparator.compare_advertisements(conn, [ad1["id"], ad2["id"]])
            self.assertEqual(result["compared_count"], 2)
            self.assertIsNotNone(result["best_ad"])
            self.assertEqual(result["results"][0]["rank"], 1)
            # 广告B CPA更低 (500/10=50 vs 300/3=100)，表现更好，应排名第一
            self.assertEqual(result["results"][0]["advertisement_title"], "广告B")
            self.assertEqual(result["best_ad"]["advertisement_title"], "广告B")

    def test_compare_empty(self):
        with get_db() as conn:
            comparator = CreativeEffectComparator()
            result = comparator.compare_advertisements(conn, [])
            self.assertEqual(result["compared_count"], 0)
            self.assertIsNone(result["best_ad"])


class ProjectOperationsReportTest(unittest.TestCase):
    """测试项目经营报告"""

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

    def test_generate_report(self):
        with get_db() as conn:
            reporter = ProjectOperationsReport()
            project, customer, product, idea, script, ad, record = _create_full_chain(conn)

            # 录入效果数据
            mgr = PerformanceDataManager()
            mgr.record_performance(conn, record["id"], views=5000, orders=3, cost_cny=300.0)

            report = reporter.generate_report(
                conn, project["id"],
                period_start="2026-10-25",
                period_end="2026-11-23",
            )
            self.assertEqual(report["project_id"], project["id"])
            self.assertEqual(report["period_start"], "2026-10-25")
            self.assertEqual(report["period_end"], "2026-11-23")
            self.assertIn("commercial_metrics", report)
            self.assertIn("content_metrics", report)
            self.assertIn("technical_metrics", report)
            self.assertIn("ad_performance", report)
            self.assertIn("summary", report)
            self.assertEqual(report["summary"]["technical_pass"], True)

    def test_report_has_summary_conclusion(self):
        with get_db() as conn:
            reporter = ProjectOperationsReport()
            project, _, _, _, _, _, _ = _create_full_chain(conn)

            report = reporter.generate_report(
                conn, project["id"],
                period_start="2026-10-25",
                period_end="2026-11-23",
            )
            summary = report["summary"]
            self.assertIn("overall_pass", summary)
            self.assertIn("conclusion", summary)
            self.assertIn("recommendation", summary)
            self.assertIn(summary["conclusion"], ["PASS", "CONDITIONAL_PASS"])


class NowISOTest(unittest.TestCase):
    """测试时间戳生成"""

    def test_now_iso(self):
        ts = now_iso()
        self.assertIsInstance(ts, str)
        self.assertIn("T", ts)


if __name__ == "__main__":
    unittest.main()
