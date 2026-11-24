"""AI Story Commerce — G6 视频生产与合规审核测试套件"""

import sys
import os
import unittest
import json
import tempfile
import shutil

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "backend", "stdlib"))

from app.db.session import get_db, init_db
import app.crud.crud as crud
from app.video_production import (
    VideoProductionManager,
    MaterialManager,
    ComplianceReviewManager,
    AdvertisementVersionManager,
    PublishingManager,
    compute_file_sha256,
    now_iso,
)
from app.video_production.adapters import (
    ImageGenerationAdapter,
    VideoGenerationAdapter,
    VoiceGenerationAdapter,
    GenerationResult,
    MockImageAdapter,
    MockVideoAdapter,
    MockVoiceAdapter,
)
from app.video_production.ffmpeg import FFmpegProcessor, FFmpegResult


def _create_full_chain(conn):
    """创建项目-商品-创意-剧本-分镜的完整链条"""
    project = crud.project_create(conn, {"name": "测试项目"})
    product = crud.product_create(conn, {
        "project_id": project["id"],
        "name": "测试商品",
        "category": "other",
    })
    idea = crud.story_idea_create(conn, {
        "product_id": product["id"],
        "title": "测试创意",
    })
    script = crud.script_create(conn, {
        "story_idea_id": idea["id"],
        "version": 1,
        "title": "测试剧本",
        "content": "剧本内容",
    })
    storyboard = crud.storyboard_create(conn, {
        "script_id": script["id"],
        "shot_number": 1,
        "description": "测试分镜",
        "image_prompt": "测试提示词",
    })
    return project, product, idea, script, storyboard


class VideoProductionManagerTest(unittest.TestCase):
    """测试视频生产任务管理"""

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

    def test_create_production_task(self):
        with get_db() as conn:
            mgr = VideoProductionManager()
            _, _, _, script, storyboard = _create_full_chain(conn)

            task = mgr.create_production_task(
                conn, storyboard["id"], "image_gen",
                input_data='{"prompt": "test"}'
            )
            self.assertIsNotNone(task["id"])
            self.assertEqual(task["task_type"], "image_gen")
            self.assertEqual(task["status"], "pending")
            self.assertEqual(task["storyboard_id"], storyboard["id"])

    def test_update_task_status(self):
        with get_db() as conn:
            mgr = VideoProductionManager()
            _, _, _, script, storyboard = _create_full_chain(conn)

            task = mgr.create_production_task(conn, storyboard["id"], "video_gen")
            updated = mgr.update_task_status(
                conn, task["id"], "completed",
                output_data='{"file": "output.mp4"}'
            )
            self.assertEqual(updated["status"], "completed")
            self.assertIsNotNone(updated["completed_at"])

    def test_list_tasks(self):
        with get_db() as conn:
            mgr = VideoProductionManager()
            _, _, _, script, storyboard = _create_full_chain(conn)

            mgr.create_production_task(conn, storyboard["id"], "image_gen")
            mgr.create_production_task(conn, storyboard["id"], "voice")

            tasks = mgr.list_tasks(conn, storyboard_id=storyboard["id"])
            self.assertEqual(len(tasks), 2)

            completed = mgr.list_tasks(conn, status="pending")
            self.assertEqual(len(completed), 2)


class MaterialManagerTest(unittest.TestCase):
    """测试素材管理"""

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

    def test_upload_and_verify_material(self):
        with get_db() as conn:
            mgr = MaterialManager()
            _, _, _, script, storyboard = _create_full_chain(conn)

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tmp.write(b"test image data")
            tmp.close()

            try:
                asset = mgr.upload_material(
                    conn, storyboard["id"], None,
                    "image", tmp.name,
                    ai_generated=True,
                    ai_disclosure=True,
                )
                self.assertIsNotNone(asset["id"])
                self.assertEqual(asset["media_type"], "image")
                self.assertEqual(asset["sha256"], compute_file_sha256(tmp.name))
                self.assertEqual(asset["ai_generated"], 1)
                self.assertEqual(asset["ai_disclosure"], 1)

                # 验证完整性
                verification = mgr.verify_material_integrity(conn, asset["id"])
                self.assertTrue(verification["verified"])
            finally:
                os.unlink(tmp.name)

    def test_list_materials_by_type(self):
        with get_db() as conn:
            mgr = MaterialManager()
            _, _, _, script, storyboard = _create_full_chain(conn)

            tmp1 = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tmp1.write(b"image data")
            tmp1.close()
            tmp2 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tmp2.write(b"audio data")
            tmp2.close()

            try:
                mgr.upload_material(conn, storyboard["id"], None, "image", tmp1.name)
                mgr.upload_material(conn, storyboard["id"], None, "audio", tmp2.name)

                images = mgr.list_materials(conn, storyboard_id=storyboard["id"], media_type="image")
                self.assertEqual(len(images), 1)

                audios = mgr.list_materials(conn, storyboard_id=storyboard["id"], media_type="audio")
                self.assertEqual(len(audios), 1)
            finally:
                os.unlink(tmp1.name)
                os.unlink(tmp2.name)


class ComplianceReviewManagerTest(unittest.TestCase):
    """测试合规审核"""

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

    def test_create_and_complete_review_passed(self):
        with get_db() as conn:
            mgr = ComplianceReviewManager()
            project = crud.project_create(conn, {"name": "测试项目"})
            ad = crud.advertisement_create(conn, {
                "project_id": project["id"],
                "version": 1,
                "title": "测试广告",
            })

            review = mgr.create_review(conn, ad["id"], reviewer_type="agent")
            self.assertEqual(review["status"], "pending")

            # 全部通过
            for item in mgr.REQUIRED_CHECKS:
                mgr.update_review_item(conn, review["id"], item, True)

            result = mgr.complete_review(conn, review["id"], "全部合规")
            self.assertEqual(result["status"], "passed")
            self.assertTrue(result["all_passed"])
            self.assertTrue(result["can_publish"])
            self.assertEqual(result["failed_items"], [])

    def test_complete_review_failed(self):
        with get_db() as conn:
            mgr = ComplianceReviewManager()
            project = crud.project_create(conn, {"name": "测试项目"})
            ad = crud.advertisement_create(conn, {
                "project_id": project["id"],
                "version": 1,
                "title": "测试广告",
            })

            review = mgr.create_review(conn, ad["id"])

            # 只通过部分项
            for item in mgr.REQUIRED_CHECKS:
                mgr.update_review_item(conn, review["id"], item, False)

            result = mgr.complete_review(conn, review["id"], "不合规")
            self.assertEqual(result["status"], "failed")
            self.assertFalse(result["all_passed"])
            self.assertFalse(result["can_publish"])
            self.assertEqual(len(result["failed_items"]), len(mgr.REQUIRED_CHECKS))

    def test_can_publish(self):
        with get_db() as conn:
            mgr = ComplianceReviewManager()
            project = crud.project_create(conn, {"name": "测试项目"})
            ad = crud.advertisement_create(conn, {
                "project_id": project["id"],
                "version": 1,
                "title": "测试广告",
            })

            # 没有审核
            can = mgr.can_publish(conn, ad["id"])
            self.assertFalse(can["can_publish"])

            # 审核通过
            review = mgr.create_review(conn, ad["id"])
            for item in mgr.REQUIRED_CHECKS:
                mgr.update_review_item(conn, review["id"], item, True)
            mgr.complete_review(conn, review["id"])

            can = mgr.can_publish(conn, ad["id"])
            self.assertTrue(can["can_publish"])

    def test_ai_disclosure_check(self):
        with get_db() as conn:
            mgr = ComplianceReviewManager()
            project = crud.project_create(conn, {"name": "测试项目"})
            ad = crud.advertisement_create(conn, {
                "project_id": project["id"],
                "version": 1,
                "title": "测试广告",
            })

            review = mgr.create_review(conn, ad["id"])
            mgr.update_review_item(conn, review["id"], "ai_disclosure_confirmed", True)

            disclosure = mgr.check_ai_disclosure(conn, ad["id"])
            self.assertTrue(disclosure["ai_disclosure_required"])
            self.assertTrue(disclosure["ai_disclosure_confirmed"])


class AdvertisementVersionManagerTest(unittest.TestCase):
    """测试广告版本管理"""

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

    def test_create_advertisement_versioning(self):
        with get_db() as conn:
            mgr = AdvertisementVersionManager()
            project = crud.project_create(conn, {"name": "测试项目"})

            # 创建第一个版本
            ad1 = mgr.create_advertisement(conn, project["id"], "广告 v1")
            self.assertEqual(ad1["version"], 1)
            self.assertEqual(ad1["is_current"], 1)

            # 创建第二个版本
            ad2 = mgr.create_advertisement(conn, project["id"], "广告 v2")
            self.assertEqual(ad2["version"], 2)
            self.assertEqual(ad2["is_current"], 1)

            # 第一版应该不再是当前
            ads = mgr.get_all_versions(conn, project["id"])
            current = [a for a in ads if a.get("is_current")]
            self.assertEqual(len(current), 1)
            self.assertEqual(current[0]["version"], 2)

    def test_get_current_advertisement(self):
        with get_db() as conn:
            mgr = AdvertisementVersionManager()
            project = crud.project_create(conn, {"name": "测试项目"})

            # 没有广告
            current = mgr.get_current_advertisement(conn, project["id"])
            self.assertIsNone(current)

            # 创建后
            ad = mgr.create_advertisement(conn, project["id"], "唯一广告")
            current = mgr.get_current_advertisement(conn, project["id"])
            self.assertIsNotNone(current)
            self.assertEqual(current["id"], ad["id"])


class PublishingManagerTest(unittest.TestCase):
    """测试发布记录"""

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

    def test_create_and_verify_publishing_record(self):
        with get_db() as conn:
            mgr = PublishingManager()
            project = crud.project_create(conn, {"name": "测试项目"})
            ad = crud.advertisement_create(conn, {
                "project_id": project["id"],
                "version": 1,
                "title": "测试广告",
            })

            record = mgr.create_publishing_record(
                conn, ad["id"], platform="douyin",
                account_name="测试账号",
                publish_url="https://douyin.com/video/123",
                ai_disclosure_posted=True,
            )
            self.assertIsNotNone(record["id"])
            self.assertEqual(record["platform"], "douyin")
            self.assertEqual(record["ai_disclosure_posted"], 1)

            # 验证 AI 标识
            verification = mgr.verify_ai_disclosure_posted(conn, record["id"])
            self.assertTrue(verification["ai_disclosure_posted"])
            self.assertEqual(verification["platform"], "douyin")

    def test_list_publishing_records(self):
        with get_db() as conn:
            mgr = PublishingManager()
            project = crud.project_create(conn, {"name": "测试项目"})
            ad = crud.advertisement_create(conn, {
                "project_id": project["id"],
                "version": 1,
                "title": "测试广告",
            })

            mgr.create_publishing_record(conn, ad["id"], platform="douyin")
            mgr.create_publishing_record(conn, ad["id"], platform="other")

            records = mgr.list_publishing_records(conn, ad["id"])
            self.assertEqual(len(records), 2)


class AdapterTest(unittest.TestCase):
    """测试生成适配器"""

    def test_mock_image_adapter(self):
        adapter = MockImageAdapter()
        result = adapter.generate("一个美丽的风景")
        self.assertTrue(result.success)
        self.assertIsNotNone(result.file_path)
        self.assertIsNotNone(result.sha256)
        self.assertEqual(adapter.get_model_name(), "mock-image-v1")

    def test_mock_video_adapter(self):
        adapter = MockVideoAdapter()
        result = adapter.generate("一个人在走路", duration_seconds=5.0)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.file_path)
        self.assertEqual(result.duration_seconds, 5.0)
        self.assertEqual(adapter.get_model_name(), "mock-video-v1")

    def test_mock_voice_adapter(self):
        adapter = MockVoiceAdapter()
        result = adapter.generate("你好，欢迎观看", voice_reference="female_cn")
        self.assertTrue(result.success)
        self.assertIsNotNone(result.file_path)
        self.assertEqual(adapter.get_model_name(), "mock-voice-v1")

    def test_adapter_interfaces(self):
        """验证适配器基类不可直接实例化"""
        with self.assertRaises(TypeError):
            ImageGenerationAdapter()


class FFmpegProcessorTest(unittest.TestCase):
    """测试 FFmpeg 处理器"""

    def test_check_available(self):
        processor = FFmpegProcessor()
        # FFmpeg 可能不存在，返回布尔值即可
        result = processor.check_available()
        self.assertIsInstance(result, bool)

    def test_ffmpeg_result_dataclass(self):
        result = FFmpegResult(success=True, output_path="/tmp/test.mp4")
        self.assertTrue(result.success)
        self.assertEqual(result.output_path, "/tmp/test.mp4")


class ComputeSHA256Test(unittest.TestCase):
    """测试 SHA256 计算"""

    def test_compute_file_sha256(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(b"content for hash test")
        tmp.close()
        try:
            h = compute_file_sha256(tmp.name)
            self.assertEqual(len(h), 64)
            self.assertTrue(all(c in "0123456789abcdef" for c in h))
        finally:
            os.unlink(tmp.name)


class NowISOTest(unittest.TestCase):
    """测试时间戳生成"""

    def test_now_iso(self):
        ts = now_iso()
        self.assertIsInstance(ts, str)
        self.assertIn("T", ts)  # ISO 格式


if __name__ == "__main__":
    unittest.main()
