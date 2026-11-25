"""AI Story Commerce — G10 虚拟人物 IP 运营测试套件

对应立项方案商业战略第二阶段：发展数字人IP公司
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
from app.ip_operations import (
    CharacterIPAsset,
    IPContentMatrix,
    MultiPlatformAccount,
    FanProfile,
    InteractionRecord,
    FanRetention,
    BrandCollaboration,
    LicensingManagement,
    MerchandiseManagement,
    IPMetricsDashboard,
    now_iso,
)


def _create_character(conn, name="阿强"):
    """创建测试人物"""
    from app.crud.crud import character_create
    return character_create(conn, {
        "name": name,
        "gender": "male",
        "age_range": "35-45",
        "is_core_ip": True,
    })


class CharacterIPAssetTest(unittest.TestCase):
    """测试人物IP资产管理"""

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

    def test_register_and_list_asset(self):
        with get_db() as conn:
            mgr = CharacterIPAsset()
            _create_character(conn, "阿强")

            asset = mgr.register_asset(
                conn, "阿强", "face_reference",
                "/data/assets/face_ref_001.png",
                asset_version="v1.0",
                description="阿强标准面部参考图",
                usage_scope="所有内容制作",
                commercial_rights="商业授权",
            )
            self.assertIsNotNone(asset)
            self.assertEqual(asset["character_name"], "阿强")
            self.assertEqual(asset["asset_category"], "face_reference")
            self.assertEqual(asset["asset_version"], "v1.0")

            assets = mgr.list_assets(conn, character_name="阿强")
            self.assertEqual(len(assets), 1)

    def test_verify_asset_consistency(self):
        with get_db() as conn:
            mgr = CharacterIPAsset()
            _create_character(conn, "阿强")

            mgr.register_asset(conn, "阿强", "face_reference",
                               "/data/face1.png", asset_version="v1.0")
            mgr.register_asset(conn, "阿强", "face_reference",
                               "/data/face2.png", asset_version="v1.0")

            check = mgr.verify_asset_consistency(conn, "阿强", "face_reference")
            self.assertTrue(check["is_consistent"])
            self.assertEqual(check["asset_count"], 2)

    def test_invalid_asset_category(self):
        with get_db() as conn:
            mgr = CharacterIPAsset()
            _create_character(conn, "阿强")

            with self.assertRaises(ValueError):
                mgr.register_asset(conn, "阿强", "invalid_category",
                                   "/data/test.png")


class IPContentMatrixTest(unittest.TestCase):
    """测试IP内容矩阵管理"""

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

    def test_create_content_item(self):
        with get_db() as conn:
            mgr = IPContentMatrix()

            content = mgr.create_content_item(
                conn, "阿强", "douyin",
                "短视频", "阿强的清洁日常",
                style="喜剧", theme="家庭矛盾",
                scheduled_time="2026-12-01T12:00:00+08:00",
            )
            self.assertIsNotNone(content)
            self.assertEqual(content["character_name"], "阿强")
            self.assertEqual(content["platform"], "douyin")
            self.assertEqual(content["content_type"], "短视频")
            self.assertEqual(content["status"], "planned")

    def test_invalid_content_type(self):
        with get_db() as conn:
            mgr = IPContentMatrix()

            with self.assertRaises(ValueError):
                mgr.create_content_item(conn, "阿强", "douyin",
                                        "无效类型", "标题")

    def test_mark_published(self):
        with get_db() as conn:
            mgr = IPContentMatrix()

            content = mgr.create_content_item(
                conn, "阿强", "douyin", "短视频", "测试标题"
            )

            result = mgr.mark_published(conn, content["content_id"],
                                        "2026-12-01T12:00:00+08:00")
            self.assertEqual(result["status"], "published")
            self.assertEqual(result["actual_publish_time"],
                             "2026-12-01T12:00:00+08:00")

    def test_list_content(self):
        with get_db() as conn:
            mgr = IPContentMatrix()

            mgr.create_content_item(conn, "阿强", "douyin", "短视频", "内容1")
            mgr.create_content_item(conn, "阿强", "bilibili", "长视频", "内容2")

            all_content = mgr.list_content(conn, character_name="阿强")
            self.assertEqual(len(all_content), 2)

            douyin_content = mgr.list_content(conn, character_name="阿强",
                                              platform="douyin")
            self.assertEqual(len(douyin_content), 1)


class MultiPlatformAccountTest(unittest.TestCase):
    """测试IP账号多平台运营"""

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

    def test_register_account(self):
        with get_db() as conn:
            mgr = MultiPlatformAccount()

            account = mgr.register_account(
                conn, "阿强", "douyin", "@阿强",
                account_url="https://douyin.com/user/xxx",
                bio="逆袭小人物阿强",
                is_verified=True,
            )
            self.assertIsNotNone(account)
            self.assertEqual(account["platform"], "douyin")
            self.assertEqual(account["account_name"], "@阿强")
            self.assertTrue(account["is_verified"])

    def test_invalid_platform(self):
        with get_db() as conn:
            mgr = MultiPlatformAccount()

            with self.assertRaises(ValueError):
                mgr.register_account(conn, "阿强", "invalid_platform", "@test")

    def test_list_accounts(self):
        with get_db() as conn:
            mgr = MultiPlatformAccount()

            mgr.register_account(conn, "阿强", "douyin", "@阿强_douyin")
            mgr.register_account(conn, "阿强", "bilibili", "@阿强_bilibili")

            all_accounts = mgr.list_accounts(conn, character_name="阿强")
            self.assertEqual(len(all_accounts), 2)

            douyin_accounts = mgr.list_accounts(conn, character_name="阿强",
                                                platform="douyin")
            self.assertEqual(len(douyin_accounts), 1)


class FanProfileTest(unittest.TestCase):
    """测试粉丝画像管理"""

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

    def test_create_fan_profile(self):
        with get_db() as conn:
            mgr = FanProfile()

            profile = mgr.create_fan_profile(
                conn, "阿强", "fan_001", "douyin",
                fan_name="张小明",
                age_group="25-35",
                gender="male",
                location="北京",
                interest_tags=["喜剧", "家居清洁"],
                follow_time="2026-11-20T10:00:00+08:00",
            )
            self.assertIsNotNone(profile)
            self.assertEqual(profile["fan_id"], "fan_001")
            self.assertEqual(profile["character_name"], "阿强")

    def test_list_fans(self):
        with get_db() as conn:
            mgr = FanProfile()

            mgr.create_fan_profile(conn, "阿强", "fan_001", "douyin",
                                   fan_name="粉丝1")
            mgr.create_fan_profile(conn, "阿强", "fan_002", "bilibili",
                                   fan_name="粉丝2")

            all_fans = mgr.list_fans(conn, character_name="阿强")
            self.assertEqual(len(all_fans), 2)


class InteractionRecordTest(unittest.TestCase):
    """测试粉丝互动记录"""

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

    def test_record_interaction(self):
        with get_db() as conn:
            mgr = InteractionRecord()

            interaction = mgr.record_interaction(
                conn, "阿强", "douyin", "fan_001",
                "like", content_id="content_001",
                content="好看！", sentiment="positive",
            )
            self.assertIsNotNone(interaction)
            self.assertEqual(interaction["interaction_type"], "like")
            self.assertEqual(interaction["sentiment"], "positive")

    def test_invalid_interaction_type(self):
        with get_db() as conn:
            mgr = InteractionRecord()

            with self.assertRaises(ValueError):
                mgr.record_interaction(conn, "阿强", "douyin", "fan_001",
                                       "invalid_type")

    def test_list_interactions(self):
        with get_db() as conn:
            mgr = InteractionRecord()

            mgr.record_interaction(conn, "阿强", "douyin", "fan_001", "like")
            mgr.record_interaction(conn, "阿强", "douyin", "fan_002", "comment")

            all_interactions = mgr.list_interactions(conn, character_name="阿强")
            self.assertEqual(len(all_interactions), 2)

            likes = mgr.list_interactions(conn, character_name="阿强",
                                          interaction_type="like")
            self.assertEqual(len(likes), 1)


class FanRetentionTest(unittest.TestCase):
    """测试粉丝留存分析"""

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

    def test_calculate_retention_rate(self):
        with get_db() as conn:
            mgr = FanRetention()

            # 创建5个粉丝，3个在指定时间段内
            mgr_fan = FanProfile()
            mgr_fan.create_fan_profile(conn, "阿强", "fan_001", "douyin",
                                       follow_time="2026-11-01T10:00:00+08:00")
            mgr_fan.create_fan_profile(conn, "阿强", "fan_002", "douyin",
                                       follow_time="2026-11-05T10:00:00+08:00")
            mgr_fan.create_fan_profile(conn, "阿强", "fan_003", "douyin",
                                       follow_time="2026-11-10T10:00:00+08:00")
            mgr_fan.create_fan_profile(conn, "阿强", "fan_004", "douyin",
                                       follow_time="2026-10-20T10:00:00+08:00")
            mgr_fan.create_fan_profile(conn, "阿强", "fan_005", "douyin",
                                       follow_time="2026-10-25T10:00:00+08:00")

            result = mgr.calculate_retention_rate(conn, "阿强",
                                                  "2026-11-01", "2026-11-30")
            self.assertEqual(result["total_fans"], 5)
            self.assertEqual(result["retained_fans"], 3)
            self.assertEqual(result["retention_rate_percent"], 60.0)


class BrandCollaborationTest(unittest.TestCase):
    """测试品牌合作管理"""

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

    def test_create_collaboration(self):
        with get_db() as conn:
            mgr = BrandCollaboration()

            collab = mgr.create_collaboration(
                conn, "阿强", "某清洁剂品牌",
                "产品植入", 50000.0,
                "2026-12-01", "2026-12-31",
                "3条短视频+2条连续剧情",
            )
            self.assertIsNotNone(collab)
            self.assertEqual(collab["character_name"], "阿强")
            self.assertEqual(collab["brand_name"], "某清洁剂品牌")
            self.assertEqual(collab["contract_amount_cny"], 50000.0)
            self.assertEqual(collab["status"], "意向")

    def test_list_collaborations(self):
        with get_db() as conn:
            mgr = BrandCollaboration()

            mgr.create_collaboration(conn, "阿强", "品牌A", "产品植入",
                                     30000.0, "2026-12-01", "2026-12-31")
            mgr.create_collaboration(conn, "阿强", "品牌B", "代言",
                                     100000.0, "2027-01-01", "2027-12-31")

            all_collabs = mgr.list_collaborations(conn, character_name="阿强")
            self.assertEqual(len(all_collabs), 2)


class LicensingManagementTest(unittest.TestCase):
    """测试IP授权管理"""

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

    def test_create_license(self):
        with get_db() as conn:
            mgr = LicensingManagement()

            license_item = mgr.create_license(
                conn, "阿强", "某玩具厂商",
                "人偶周边授权", 200000.0,
                "2027-01-01", "2027-12-31",
                "中国大陆",
            )
            self.assertIsNotNone(license_item)
            self.assertEqual(license_item["licensee"], "某玩具厂商")
            self.assertEqual(license_item["license_fee_cny"], 200000.0)

    def test_list_licenses(self):
        with get_db() as conn:
            mgr = LicensingManagement()

            mgr.create_license(conn, "阿强", "厂商A", "人偶授权", 100000.0,
                               "2027-01-01", "2027-12-31")
            mgr.create_license(conn, "阿强", "厂商B", "服装授权", 150000.0,
                               "2027-02-01", "2028-01-31")

            licenses = mgr.list_licenses(conn, character_name="阿强")
            self.assertEqual(len(licenses), 2)


class MerchandiseManagementTest(unittest.TestCase):
    """测试IP周边管理"""

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

    def test_create_merchandise(self):
        with get_db() as conn:
            mgr = MerchandiseManagement()

            merch = mgr.create_merchandise(
                conn, "阿强", "阿强公仔",
                "玩偶", 99.0, 40.0, 500,
                "阿强正版公仔周边",
            )
            self.assertIsNotNone(merch)
            self.assertEqual(merch["product_name"], "阿强公仔")
            self.assertEqual(merch["price_cny"], 99.0)
            self.assertEqual(merch["inventory"], 500)

    def test_list_merchandise(self):
        with get_db() as conn:
            mgr = MerchandiseManagement()

            mgr.create_merchandise(conn, "阿强", "阿强T恤", "服装", 89.0, 30.0, 200)
            mgr.create_merchandise(conn, "阿强", "阿强马克杯", "杯子", 39.0, 15.0, 300)

            all_merch = mgr.list_merchandise(conn, character_name="阿强")
            self.assertEqual(len(all_merch), 2)


class IPMetricsDashboardTest(unittest.TestCase):
    """测试IP数据看板与运营指标"""

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

    def test_calculate_fan_growth(self):
        with get_db() as conn:
            mgr = IPMetricsDashboard()
            fan_mgr = FanProfile()

            fan_mgr.create_fan_profile(conn, "阿强", "fan_001", "douyin",
                                       follow_time="2026-11-01T10:00:00+08:00")
            fan_mgr.create_fan_profile(conn, "阿强", "fan_002", "douyin",
                                       follow_time="2026-11-15T10:00:00+08:00")

            result = mgr.calculate_fan_growth(conn, "阿强",
                                              "2026-11-01", "2026-11-30")
            self.assertEqual(result["total_fans"], 2)
            self.assertEqual(result["new_fans_in_period"], 2)

    def test_calculate_interaction_rate(self):
        with get_db() as conn:
            mgr = IPMetricsDashboard()
            fan_mgr = FanProfile()
            inter_mgr = InteractionRecord()

            fan_mgr.create_fan_profile(conn, "阿强", "fan_001", "douyin")
            fan_mgr.create_fan_profile(conn, "阿强", "fan_002", "douyin")
            fan_mgr.create_fan_profile(conn, "阿强", "fan_003", "douyin")

            inter_mgr.record_interaction(conn, "阿强", "douyin", "fan_001", "like")
            inter_mgr.record_interaction(conn, "阿强", "douyin", "fan_002", "comment")
            inter_mgr.record_interaction(conn, "阿强", "douyin", "fan_003", "share")

            result = mgr.calculate_interaction_rate(conn, "阿强")
            self.assertEqual(result["total_interactions"], 3)
            self.assertEqual(result["total_fans"], 3)
            self.assertEqual(result["interaction_rate_percent"], 100.0)

    def test_calculate_ip_commercial_value(self):
        with get_db() as conn:
            mgr = IPMetricsDashboard()
            collab_mgr = BrandCollaboration()
            lic_mgr = LicensingManagement()
            merch_mgr = MerchandiseManagement()

            collab_mgr.create_collaboration(conn, "阿强", "品牌A", "产品植入",
                                            50000.0, "2026-12-01", "2026-12-31")
            collab_mgr.create_collaboration(conn, "阿强", "品牌B", "代言",
                                            100000.0, "2027-01-01", "2027-12-31",
                                            status="已签约")

            lic_mgr.create_license(conn, "阿强", "厂商A", "人偶授权", 200000.0,
                                   "2027-01-01", "2027-12-31")

            merch_mgr.create_merchandise(conn, "阿强", "阿强公仔", "玩偶",
                                         99.0, 40.0, 100)

            result = mgr.calculate_ip_commercial_value(conn, "阿强")
            self.assertEqual(result["brand_collaboration_revenue_cny"], 100000.0)
            self.assertEqual(result["licensing_revenue_cny"], 200000.0)
            self.assertEqual(result["merchandise_potential_revenue_cny"], 9900.0)
            self.assertEqual(result["total_commercial_value_cny"], 309900.0)

    def test_generate_ip_dashboard(self):
        with get_db() as conn:
            mgr = IPMetricsDashboard()

            dashboard = mgr.generate_ip_dashboard(conn, "阿强")
            self.assertEqual(dashboard["character_name"], "阿强")
            self.assertIn("fan_growth", dashboard)
            self.assertIn("interaction_rate", dashboard)
            self.assertIn("commercial_value", dashboard)


if __name__ == "__main__":
    unittest.main()
