"""AI Story Commerce — G9 商业化扩张测试套件

对应立项方案商业战略第一阶段：先做AI剧情广告服务公司
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
from app.commercial_expansion import (
    CustomerProfile,
    ContactRecord,
    SalesOpportunity,
    ServiceProduct,
    ContractManagement,
    SampleAd,
    CharacterIPAccount,
    ContentPublishingPlan,
    BusinessMetrics,
    now_iso,
)


def _create_customer(conn):
    """创建测试客户"""
    return crud.customer_create(conn, {
        "name": "测试商家",
        "contact_person": "张三",
        "phone": "13800000000",
    })


class CustomerProfileTest(unittest.TestCase):
    """测试商家客户画像管理"""

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

    def test_create_customer_profile(self):
        with get_db() as conn:
            mgr = CustomerProfile()
            customer = _create_customer(conn)

            profile = mgr.create_customer_profile(
                conn, customer["id"],
                category="中小品牌",
                industry="家居清洁",
                business_scale="小型",
                annual_revenue_cny=500000.0,
                preferred_categories=["家居清洁", "日用百货"],
                compliance_preference="不夸大功效",
            )
            self.assertIsNotNone(profile)
            self.assertEqual(profile["customer_id"], customer["id"])
            self.assertEqual(profile["category"], "中小品牌")
            self.assertEqual(profile["industry"], "家居清洁")

    def test_get_customer_profile(self):
        with get_db() as conn:
            mgr = CustomerProfile()
            customer = _create_customer(conn)

            mgr.create_customer_profile(conn, customer["id"], category="电商经营者")
            profile = mgr.get_customer_profile(conn, customer["id"])
            self.assertIsNotNone(profile)
            self.assertEqual(profile["category"], "电商经营者")

    def test_invalid_category(self):
        with get_db() as conn:
            mgr = CustomerProfile()
            customer = _create_customer(conn)

            with self.assertRaises(ValueError):
                mgr.create_customer_profile(conn, customer["id"], category="无效类别")


class ContactRecordTest(unittest.TestCase):
    """测试商家联系记录"""

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

    def test_create_contact_record(self):
        with get_db() as conn:
            mgr = ContactRecord()
            customer = _create_customer(conn)

            record = mgr.create_contact_record(
                conn, customer["id"],
                contact_time="2026-11-20T10:00:00+08:00",
                channel="微信",
                content="介绍AI剧情广告服务",
                outcome="有意向",
                next_action="发送样片",
                next_action_time="2026-11-22T10:00:00+08:00",
            )
            self.assertIsNotNone(record)
            self.assertEqual(record["channel"], "微信")
            self.assertEqual(record["outcome"], "有意向")

    def test_list_contact_records(self):
        with get_db() as conn:
            mgr = ContactRecord()
            customer = _create_customer(conn)

            mgr.create_contact_record(conn, customer["id"],
                                      contact_time="2026-11-20T10:00:00+08:00",
                                      channel="电话", content="初次联系",
                                      outcome="待跟进")
            mgr.create_contact_record(conn, customer["id"],
                                      contact_time="2026-11-21T10:00:00+08:00",
                                      channel="微信", content="发送样片",
                                      outcome="有意向")

            records = mgr.list_contact_records(conn, customer_id=customer["id"])
            self.assertEqual(len(records), 2)


class SalesOpportunityTest(unittest.TestCase):
    """测试商机跟踪"""

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

    def test_create_and_update_opportunity(self):
        with get_db() as conn:
            mgr = SalesOpportunity()
            customer = _create_customer(conn)

            opp = mgr.create_opportunity(
                conn, customer["id"],
                stage="初次接触",
                estimated_value_cny=5000.0,
                source="抖音样片",
            )
            self.assertIsNotNone(opp)
            self.assertEqual(opp["stage"], "初次接触")

            updated = mgr.update_opportunity_stage(conn, opp["opportunity_id"], "已签约")
            self.assertEqual(updated["stage"], "已签约")

    def test_list_opportunities_by_stage(self):
        with get_db() as conn:
            mgr = SalesOpportunity()
            customer = _create_customer(conn)

            mgr.create_opportunity(conn, customer["id"], stage="初次接触")
            mgr.create_opportunity(conn, customer["id"], stage="已签约")

            opps = mgr.list_opportunities(conn, stage="已签约")
            self.assertEqual(len(opps), 1)


class ServiceProductTest(unittest.TestCase):
    """测试商业化定价与报价系统"""

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

    def test_list_service_products(self):
        with get_db() as conn:
            mgr = ServiceProduct()
            products = mgr.list_service_products()
            self.assertEqual(len(products), 3)
            names = [p["name"] for p in products]
            self.assertIn("创意试单", names)
            self.assertIn("标准广告", names)
            self.assertIn("系列广告", names)

    def test_create_and_list_quote(self):
        with get_db() as conn:
            mgr = ServiceProduct()
            customer = _create_customer(conn)

            quote = mgr.create_quote(
                conn, customer["id"],
                product_name="标准广告",
                quoted_price_cny=6000.0,
                ad_count=5,
                revision_count=2,
                delivery_deadline="2026-12-01",
            )
            self.assertIsNotNone(quote)
            self.assertEqual(quote["status"], "pending")

            quotes = mgr.list_quotes(conn, customer_id=customer["id"])
            self.assertEqual(len(quotes), 1)


class ContractManagementTest(unittest.TestCase):
    """测试合同管理"""

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

    def test_create_and_update_contract(self):
        with get_db() as conn:
            mgr = ContractManagement()
            customer = _create_customer(conn)
            sp_mgr = ServiceProduct()
            quote = sp_mgr.create_quote(
                conn, customer["id"],
                product_name="标准广告",
                quoted_price_cny=6000.0,
                ad_count=5,
                revision_count=2,
                delivery_deadline="2026-12-01",
            )

            contract = mgr.create_contract(
                conn, customer["id"],
                quote_id=quote["quote_id"],
                contract_amount_cny=6000.0,
                payment_terms="预付50%，交付后付50%",
                ad_delivery_count=5,
                contract_start_date="2026-11-20",
                contract_end_date="2026-12-10",
            )
            self.assertIsNotNone(contract)
            self.assertEqual(contract["status"], "草稿")

            updated = mgr.update_contract_status(
                conn, contract["contract_id"],
                status="已签署",
                payment_status="部分付款",
            )
            self.assertEqual(updated["status"], "已签署")
            self.assertEqual(updated["payment_status"], "部分付款")

    def test_list_contracts(self):
        with get_db() as conn:
            mgr = ContractManagement()
            sp_mgr = ServiceProduct()
            customer = _create_customer(conn)

            quote = sp_mgr.create_quote(conn, customer["id"], "标准广告", 6000.0, 5, 2, "2026-12-01")
            mgr.create_contract(conn, customer["id"], quote["quote_id"], 6000.0,
                                "预付50%", 5, "2026-11-20", "2026-12-10")

            contracts = mgr.list_contracts(conn, status="草稿")
            self.assertEqual(len(contracts), 1)


class SampleAdTest(unittest.TestCase):
    """测试样片与作品集管理"""

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

    def test_create_and_list_sample_ad(self):
        with get_db() as conn:
            mgr = SampleAd()

            sample = mgr.create_sample_ad(
                conn, ad_title="家居清洁样片",
                ad_file_path="/data/outputs/sample1.mp4",
                ad_sha256="abc123def456",
                product_category="家居清洁",
                industry="家居清洁",
                story_type="误会型",
                character_name="阿强",
                views=5000,
                orders=3,
                cost_cny=300.0,
                is_featured=True,
            )
            self.assertIsNotNone(sample)
            self.assertTrue(sample["is_featured"])

            samples = mgr.list_sample_ads(conn, featured_only=True)
            self.assertEqual(len(samples), 1)
            self.assertEqual(samples[0]["ad_title"], "家居清洁样片")

    def test_update_sample_metrics(self):
        with get_db() as conn:
            mgr = SampleAd()

            sample = mgr.create_sample_ad(
                conn, ad_title="测试样片",
                ad_file_path="/data/outputs/sample.mp4",
                ad_sha256="abc123",
                product_category="日用百货",
                industry="日用百货",
                story_type="反转型",
            )

            updated = mgr.update_sample_metrics(
                conn, sample["sample_id"],
                views=10000, orders=10, cost_cny=500.0,
            )
            self.assertEqual(updated["views"], 10000)
            self.assertEqual(updated["orders"], 10)
            self.assertEqual(updated["cost_cny"], 500.0)


class CharacterIPAccountTest(unittest.TestCase):
    """测试核心人物IP运营"""

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

    def test_create_ip_account(self):
        with get_db() as conn:
            mgr = CharacterIPAccount()

            account = mgr.create_ip_account(
                conn, character_name="阿强",
                platform="douyin",
                account_name="@阿强",
                follower_count=10000,
                total_views=500000,
                total_likes=30000,
            )
            self.assertIsNotNone(account)
            self.assertEqual(account["platform"], "douyin")
            self.assertEqual(account["follower_count"], 10000)

    def test_update_ip_account_metrics(self):
        with get_db() as conn:
            mgr = CharacterIPAccount()

            account = mgr.create_ip_account(
                conn, character_name="阿强",
                platform="douyin",
                account_name="@阿强",
            )

            updated = mgr.update_ip_account_metrics(
                conn, account["account_id"],
                follower_count=15000,
                total_views=800000,
            )
            self.assertEqual(updated["follower_count"], 15000)
            self.assertEqual(updated["total_views"], 800000)


class ContentPublishingPlanTest(unittest.TestCase):
    """测试内容发布计划"""

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

    def test_create_publishing_plan(self):
        with get_db() as conn:
            mgr = CharacterIPAccount()
            cp_mgr = ContentPublishingPlan()

            account = mgr.create_ip_account(
                conn, character_name="阿强",
                platform="douyin",
                account_name="@阿强",
            )

            plan = cp_mgr.create_publishing_plan(
                conn, account["account_id"],
                content_title="阿强的清洁日常",
                content_type="短视频",
                scheduled_publish_time="2026-12-01T12:00:00+08:00",
                story_type="误会型",
                product_category="家居清洁",
            )
            self.assertIsNotNone(plan)
            self.assertEqual(plan["status"], "pending")

            plans = cp_mgr.list_publishing_plans(conn, status="pending")
            self.assertEqual(len(plans), 1)


class BusinessMetricsTest(unittest.TestCase):
    """测试商业化运营指标"""

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

    def test_calculate_cac(self):
        with get_db() as conn:
            mgr = BusinessMetrics()
            cac = mgr.calculate_cac(conn, total_acquisition_cost_cny=5000.0, new_customers=10)
            self.assertEqual(cac, 500.0)

    def test_calculate_aov(self):
        with get_db() as conn:
            mgr = BusinessMetrics()
            aov = mgr.calculate_aov(conn, total_revenue_cny=30000.0, total_orders=5)
            self.assertEqual(aov, 6000.0)

    def test_calculate_repeat_rate(self):
        with get_db() as conn:
            mgr = BusinessMetrics()
            rate = mgr.calculate_repeat_rate(conn, repeat_customers=3, total_customers=10)
            self.assertEqual(rate, 30.0)

    def test_calculate_roi(self):
        with get_db() as conn:
            mgr = BusinessMetrics()
            roi = mgr.calculate_roi(conn, total_revenue_cny=15000.0, total_cost_cny=5000.0)
            self.assertEqual(roi, 200.0)

    def test_generate_business_dashboard(self):
        with get_db() as conn:
            mgr = BusinessMetrics()
            sp_mgr = ServiceProduct()
            cm_mgr = ContractManagement()
            customer = _create_customer(conn)

            quote = sp_mgr.create_quote(conn, customer["id"], "标准广告", 6000.0, 5, 2, "2026-12-01")
            contract = cm_mgr.create_contract(conn, customer["id"], quote["quote_id"], 6000.0,
                                   "预付50%", 5, "2026-11-20", "2026-12-10")
            cm_mgr.update_contract_status(conn, contract["contract_id"], "已签署", "已付款")

            dashboard = mgr.generate_business_dashboard(conn)
            self.assertIn("customer_metrics", dashboard)
            self.assertIn("revenue_metrics", dashboard)
            self.assertIn("ip_metrics", dashboard)
            self.assertIn("content_metrics", dashboard)
            self.assertEqual(dashboard["revenue_metrics"]["total_orders"], 1)


if __name__ == "__main__":
    unittest.main()
