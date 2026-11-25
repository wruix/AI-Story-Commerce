"""AI Story Commerce — G11 SaaS 产品化测试套件

对应立项方案商业战略第三阶段：将内部生产能力产品化为SaaS
"""

import sys
import os
import unittest
import json
import tempfile

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "backend", "stdlib"))

from app.db.session import get_db, init_db
from app.saas import (
    Tenant,
    SubscriptionPlan,
    Subscription,
    PaymentMethod,
    Invoice,
    ApiKey,
    Webhook,
    UsageMeter,
    AdminDashboard,
    now_iso,
)


def _create_tenant(conn):
    """创建测试租户"""
    mgr = Tenant()
    return mgr.create_tenant(
        conn, "测试租户", "test-tenant",
        plan="professional",
        status="active",
        owner_email="test@example.com",
        company_name="测试公司",
    )


class TenantTest(unittest.TestCase):
    """测试多租户管理"""

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

    def test_create_tenant(self):
        with get_db() as conn:
            mgr = Tenant()

            tenant = mgr.create_tenant(
                conn, "测试租户", "test-tenant",
                plan="professional",
                status="active",
                owner_email="test@example.com",
                company_name="测试公司",
                custom_domain="test.example.com",
            )
            self.assertIsNotNone(tenant)
            self.assertEqual(tenant["tenant_name"], "测试租户")
            self.assertEqual(tenant["subdomain"], "test-tenant")
            self.assertEqual(tenant["plan"], "professional")
            self.assertEqual(tenant["status"], "active")

    def test_list_tenants(self):
        with get_db() as conn:
            mgr = Tenant()

            mgr.create_tenant(conn, "租户A", "tenant-a", plan="starter", status="active")
            mgr.create_tenant(conn, "租户B", "tenant-b", plan="professional", status="trial")

            all_tenants = mgr.list_tenants(conn)
            self.assertEqual(len(all_tenants), 2)

            active_tenants = mgr.list_tenants(conn, status="active")
            self.assertEqual(len(active_tenants), 1)

    def test_update_tenant(self):
        with get_db() as conn:
            mgr = Tenant()

            tenant = mgr.create_tenant(conn, "租户", "tenant-test", plan="starter", status="active")

            updated = mgr.update_tenant(conn, tenant["tenant_id"], status="suspended", plan="professional")
            self.assertEqual(updated["status"], "suspended")
            self.assertEqual(updated["plan"], "professional")

    def test_invalid_plan(self):
        with get_db() as conn:
            mgr = Tenant()

            with self.assertRaises(ValueError):
                mgr.create_tenant(conn, "租户", "tenant-test", plan="invalid_plan")


class SubscriptionPlanTest(unittest.TestCase):
    """测试订阅套餐定义"""

    def test_list_plans(self):
        mgr = SubscriptionPlan()
        plans = mgr.list_plans()
        self.assertEqual(len(plans), 3)
        names = [p["plan_name"] for p in plans]
        self.assertIn("starter", names)
        self.assertIn("professional", names)
        self.assertIn("enterprise", names)

    def test_get_plan(self):
        mgr = SubscriptionPlan()
        plan = mgr.get_plan("professional")
        self.assertIsNotNone(plan)
        self.assertEqual(plan["plan_name"], "professional")
        self.assertEqual(plan["price_cny"], 299.0)

        nonexistent = mgr.get_plan("nonexistent")
        self.assertIsNone(nonexistent)


class SubscriptionTest(unittest.TestCase):
    """测试订阅管理"""

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

    def test_create_subscription(self):
        with get_db() as conn:
            mgr = Subscription()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            sub = mgr.create_subscription(
                conn, tenant["tenant_id"],
                plan_name="professional",
                price_cny=299.0,
                billing_cycle="month",
            )
            self.assertIsNotNone(sub)
            self.assertEqual(sub["tenant_id"], tenant["tenant_id"])
            self.assertEqual(sub["plan_name"], "professional")
            self.assertEqual(sub["status"], "trialing")

    def test_list_subscriptions(self):
        with get_db() as conn:
            mgr = Subscription()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            mgr.create_subscription(conn, tenant["tenant_id"], "starter", 99.0)
            mgr.create_subscription(conn, tenant["tenant_id"], "professional", 299.0)

            subs = mgr.list_subscriptions(conn, tenant_id=tenant["tenant_id"])
            self.assertEqual(len(subs), 2)

    def test_update_subscription_status(self):
        with get_db() as conn:
            mgr = Subscription()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            sub = mgr.create_subscription(conn, tenant["tenant_id"], "starter", 99.0)

            updated = mgr.update_subscription_status(conn, sub["subscription_id"], "active")
            self.assertEqual(updated["status"], "active")

    def test_invalid_status(self):
        with get_db() as conn:
            mgr = Subscription()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            with self.assertRaises(ValueError):
                mgr.create_subscription(conn, tenant["tenant_id"], "starter", 99.0,
                                        status="invalid_status")


class PaymentMethodTest(unittest.TestCase):
    """测试支付方式管理"""

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

    def test_add_payment_method(self):
        with get_db() as conn:
            mgr = PaymentMethod()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            pm = mgr.add_payment_method(
                conn, tenant["tenant_id"],
                payment_type="alipay",
                account_last4="1234",
                is_default=True,
            )
            self.assertIsNotNone(pm)
            self.assertEqual(pm["payment_type"], "alipay")
            self.assertTrue(pm["is_default"])

    def test_invalid_payment_type(self):
        with get_db() as conn:
            mgr = PaymentMethod()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            with self.assertRaises(ValueError):
                mgr.add_payment_method(conn, tenant["tenant_id"], payment_type="crypto")

    def test_list_payment_methods(self):
        with get_db() as conn:
            mgr = PaymentMethod()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            mgr.add_payment_method(conn, tenant["tenant_id"], "alipay", "1234")
            mgr.add_payment_method(conn, tenant["tenant_id"], "wechat_pay", "5678")

            pms = mgr.list_payment_methods(conn, tenant["tenant_id"])
            self.assertEqual(len(pms), 2)


class InvoiceTest(unittest.TestCase):
    """测试发票管理"""

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

    def test_create_invoice(self):
        with get_db() as conn:
            mgr = Invoice()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            inv = mgr.create_invoice(
                conn, tenant["tenant_id"],
                amount_cny=1000.0,
                tax_amount_cny=100.0,
                invoice_title="测试公司",
                tax_id="911100000000000000",
            )
            self.assertIsNotNone(inv)
            self.assertEqual(inv["amount_cny"], 1000.0)
            self.assertEqual(inv["tax_amount_cny"], 100.0)
            self.assertEqual(inv["total_cny"], 1100.0)
            self.assertEqual(inv["status"], "draft")

    def test_list_invoices(self):
        with get_db() as conn:
            mgr = Invoice()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            mgr.create_invoice(conn, tenant["tenant_id"], 1000.0, 100.0, "公司A")
            mgr.create_invoice(conn, tenant["tenant_id"], 2000.0, 200.0, "公司B")

            invs = mgr.list_invoices(conn, tenant_id=tenant["tenant_id"])
            self.assertEqual(len(invs), 2)


class ApiKeyTest(unittest.TestCase):
    """测试API密钥管理"""

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

    def test_create_api_key(self):
        with get_db() as conn:
            mgr = ApiKey()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            key = mgr.create_api_key(
                conn, tenant["tenant_id"],
                key_name="测试密钥",
                rate_limit_per_minute=100,
                quota_per_month=10000,
                scopes=["read", "write"],
            )
            self.assertIsNotNone(key)
            self.assertEqual(key["tenant_id"], tenant["tenant_id"])
            self.assertEqual(key["key_name"], "测试密钥")
            self.assertTrue(key["key_prefix"] == "asc_")
            self.assertIsNotNone(key["raw_key"])
            self.assertEqual(len(key["key_hash"]), 32)

    def test_list_api_keys(self):
        with get_db() as conn:
            mgr = ApiKey()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            mgr.create_api_key(conn, tenant["tenant_id"], "密钥1")
            mgr.create_api_key(conn, tenant["tenant_id"], "密钥2")

            keys = mgr.list_api_keys(conn, tenant["tenant_id"])
            self.assertEqual(len(keys), 2)
            # Verify raw_key is not exposed
            for key in keys:
                self.assertNotIn("raw_key", key)


class WebhookTest(unittest.TestCase):
    """测试Webhook管理"""

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

    def test_create_webhook(self):
        with get_db() as conn:
            mgr = Webhook()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            wh = mgr.create_webhook(
                conn, tenant["tenant_id"],
                url="https://example.com/webhook",
                event_types=["ad.published", "payment.succeeded"],
                secret="whsec_test123",
            )
            self.assertIsNotNone(wh)
            self.assertEqual(wh["url"], "https://example.com/webhook")
            self.assertTrue(wh["is_active"])

    def test_list_webhooks(self):
        with get_db() as conn:
            mgr = Webhook()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            mgr.create_webhook(conn, tenant["tenant_id"], "https://a.com/wh")
            mgr.create_webhook(conn, tenant["tenant_id"], "https://b.com/wh")

            whs = mgr.list_webhooks(conn, tenant["tenant_id"])
            self.assertEqual(len(whs), 2)
            # Verify secret is not exposed
            for wh in whs:
                self.assertNotIn("secret", wh)


class UsageMeterTest(unittest.TestCase):
    """测试用量计量"""

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

    def test_record_usage(self):
        with get_db() as conn:
            mgr = UsageMeter()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            usage = mgr.record_usage(
                conn, tenant["tenant_id"],
                meter_type="api_call",
                quantity=100,
                metadata='{"endpoint": "/api/v1/ads"}',
            )
            self.assertIsNotNone(usage)
            self.assertEqual(usage["meter_type"], "api_call")
            self.assertEqual(usage["quantity"], 100)

    def test_invalid_meter_type(self):
        with get_db() as conn:
            mgr = UsageMeter()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            with self.assertRaises(ValueError):
                mgr.record_usage(conn, tenant["tenant_id"], meter_type="invalid_type", quantity=1)

    def test_get_usage_summary(self):
        with get_db() as conn:
            mgr = UsageMeter()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            mgr.record_usage(conn, tenant["tenant_id"], "api_call", 50)
            mgr.record_usage(conn, tenant["tenant_id"], "api_call", 30)

            summary = mgr.get_usage_summary(conn, tenant["tenant_id"], "api_call",
                                            "2026-01-01", "2026-12-31")
            self.assertEqual(summary["total_quantity"], 80)
            self.assertEqual(summary["record_count"], 2)

    def test_list_usage(self):
        with get_db() as conn:
            mgr = UsageMeter()
            tenant_mgr = Tenant()
            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            mgr.record_usage(conn, tenant["tenant_id"], "api_call", 10)
            mgr.record_usage(conn, tenant["tenant_id"], "ad_generated", 5)

            api_calls = mgr.list_usage(conn, tenant["tenant_id"], meter_type="api_call")
            self.assertEqual(len(api_calls), 1)
            self.assertEqual(api_calls[0]["quantity"], 10)


class AdminDashboardTest(unittest.TestCase):
    """测试SaaS管理员后台"""

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

    def test_get_tenant_overview(self):
        with get_db() as conn:
            mgr = AdminDashboard()
            tenant_mgr = Tenant()

            tenant_mgr.create_tenant(conn, "租户A", "tenant-a", plan="starter", status="active")
            tenant_mgr.create_tenant(conn, "租户B", "tenant-b", plan="professional", status="trial")
            tenant_mgr.create_tenant(conn, "租户C", "tenant-c", plan="enterprise", status="active")

            overview = mgr.get_tenant_overview(conn)
            self.assertEqual(overview["total_tenants"], 3)
            self.assertEqual(overview["active_tenants"], 2)
            self.assertEqual(overview["trial_tenants"], 1)
            self.assertEqual(overview["plan_distribution"]["starter"], 1)
            self.assertEqual(overview["plan_distribution"]["professional"], 1)
            self.assertEqual(overview["plan_distribution"]["enterprise"], 1)

    def test_get_revenue_analysis(self):
        with get_db() as conn:
            mgr = AdminDashboard()
            inv_mgr = Invoice()
            sub_mgr = Subscription()
            tenant_mgr = Tenant()

            tenant = tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            inv_mgr.create_invoice(conn, tenant["tenant_id"], 1000.0, 100.0, "公司A", status="paid")
            inv_mgr.create_invoice(conn, tenant["tenant_id"], 2000.0, 200.0, "公司B", status="draft")

            sub_mgr.create_subscription(conn, tenant["tenant_id"], "starter", 99.0, status="active")
            sub_mgr.create_subscription(conn, tenant["tenant_id"], "professional", 299.0, status="trialing")

            analysis = mgr.get_revenue_analysis(conn)
            self.assertEqual(analysis["total_invoiced_cny"], 1100.0)
            self.assertEqual(analysis["total_subscriptions"], 2)
            self.assertEqual(analysis["active_subscriptions"], 1)
            self.assertEqual(analysis["paid_invoice_count"], 1)

    def test_get_system_metrics(self):
        with get_db() as conn:
            mgr = AdminDashboard()
            tenant_mgr = Tenant()

            tenant_mgr.create_tenant(conn, "租户A", "tenant-a")
            tenant_mgr.create_tenant(conn, "租户B", "tenant-b")

            metrics = mgr.get_system_metrics(conn)
            self.assertIn("tenant", metrics["resource_counts"])
            self.assertEqual(metrics["resource_counts"]["tenant"], 2)
            self.assertEqual(metrics["total_events"], 2)

    def test_get_admin_dashboard(self):
        with get_db() as conn:
            mgr = AdminDashboard()
            tenant_mgr = Tenant()
            tenant_mgr.create_tenant(conn, "测试租户", "test-tenant")

            dashboard = mgr.get_admin_dashboard(conn)
            self.assertIn("generated_at", dashboard)
            self.assertIn("tenant_overview", dashboard)
            self.assertIn("revenue_analysis", dashboard)
            self.assertIn("system_metrics", dashboard)


if __name__ == "__main__":
    unittest.main()
