"""AI Story Commerce — Backend Test Suite (stdlib unittest)"""

import json
import sys
import os
import unittest
import tempfile

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "backend", "stdlib"))

from app.db.session import get_db, init_db, generate_id, now_iso
import app.crud.crud as crud


class DatabaseTestCase(unittest.TestCase):
    """Base test case using an in-memory sqlite database."""

    def setUp(self):
        # Use a temp file database for each test
        self._db_fd, self._db_path = tempfile.mkstemp(suffix=".db")
        # Patch DATABASE_PATH to use temp file
        import app.db.session as session
        self._orig_db_path = session.DATABASE_PATH
        import pathlib
        session.DATABASE_PATH = pathlib.Path(self._db_path)
        init_db()

    def tearDown(self):
        import app.db.session as session
        session.DATABASE_PATH = self._orig_db_path
        os.close(self._db_fd)
        os.unlink(self._db_path)


class ProjectCRUDTest(DatabaseTestCase):
    """Test project CRUD operations."""

    def test_create_and_get_project(self):
        with get_db() as conn:
            obj = crud.project_create(conn, {
                "name": "测试项目",
                "description": "一个测试项目",
                "status": "active",
                "budget_cny": 5000.0,
            })
            self.assertIsNotNone(obj["id"])
            self.assertEqual(obj["name"], "测试项目")
            self.assertEqual(obj["status"], "active")

            fetched = crud.project_get(conn, obj["id"])
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched["name"], "测试项目")

    def test_list_projects(self):
        with get_db() as conn:
            for i in range(5):
                crud.project_create(conn, {"name": f"项目{i}"})
            objs = crud.project_list(conn, skip=0, limit=10)
            self.assertEqual(len(objs), 5)

    def test_update_project(self):
        with get_db() as conn:
            obj = crud.project_create(conn, {"name": "原名", "status": "draft"})
            updated = crud.project_update(conn, obj["id"], {"name": "新名", "status": "active"})
            self.assertEqual(updated["name"], "新名")
            self.assertEqual(updated["status"], "active")

    def test_delete_project(self):
        with get_db() as conn:
            obj = crud.project_create(conn, {"name": "待删除"})
            result = crud.project_delete(conn, obj["id"])
            self.assertIsNotNone(result)
            fetched = crud.project_get(conn, obj["id"])
            self.assertIsNone(fetched)


class CustomerCRUDTest(DatabaseTestCase):
    """Test customer CRUD operations."""

    def test_create_customer(self):
        with get_db() as conn:
            obj = crud.customer_create(conn, {
                "name": "测试商家",
                "contact_person": "张三",
                "phone": "13800000000",
                "email": "test@example.com",
            })
            self.assertIsNotNone(obj["id"])
            self.assertEqual(obj["name"], "测试商家")

    def test_list_customers(self):
        with get_db() as conn:
            crud.customer_create(conn, {"name": "商家A"})
            crud.customer_create(conn, {"name": "商家B"})
            objs = crud.customer_list(conn)
            self.assertEqual(len(objs), 2)


class ProductCRUDTest(DatabaseTestCase):
    """Test product CRUD operations."""

    def test_create_product(self):
        with get_db() as conn:
            # First create a project
            project = crud.project_create(conn, {"name": "测试项目"})
            obj = crud.product_create(conn, {
                "project_id": project["id"],
                "name": "测试商品",
                "category": "home_cleaning",
                "price_cny": 99.0,
            })
            self.assertIsNotNone(obj["id"])
            self.assertEqual(obj["project_id"], project["id"])
            self.assertEqual(obj["category"], "home_cleaning")

    def test_list_products_by_project(self):
        with get_db() as conn:
            project = crud.project_create(conn, {"name": "测试项目"})
            crud.product_create(conn, {"project_id": project["id"], "name": "商品A"})
            crud.product_create(conn, {"project_id": project["id"], "name": "商品B"})
            objs = crud.product_list(conn, project_id=project["id"])
            self.assertEqual(len(objs), 2)


class CharacterCRUDTest(DatabaseTestCase):
    """Test character CRUD operations."""

    def test_create_character(self):
        with get_db() as conn:
            obj = crud.character_create(conn, {
                "name": "阿强",
                "gender": "male",
                "age_range": "35-45",
                "is_core_ip": True,
            })
            self.assertIsNotNone(obj["id"])
            self.assertEqual(obj["name"], "阿强")
            self.assertEqual(obj["is_core_ip"], 1)

    def test_get_core_ip(self):
        with get_db() as conn:
            crud.character_create(conn, {"name": "角色A", "gender": "female", "is_core_ip": False})
            crud.character_create(conn, {"name": "阿强", "gender": "male", "is_core_ip": True})
            core = crud.character_get_core_ip(conn)
            self.assertIsNotNone(core)
            self.assertEqual(core["name"], "阿强")


class StoryIdeaCRUDTest(DatabaseTestCase):
    """Test story idea CRUD operations."""

    def test_create_story_idea(self):
        with get_db() as conn:
            project = crud.project_create(conn, {"name": "测试项目"})
            product = crud.product_create(conn, {
                "project_id": project["id"],
                "name": "测试商品",
                "category": "daily_goods",
            })
            obj = crud.story_idea_create(conn, {
                "product_id": product["id"],
                "title": "误会型创意",
                "story_type": "误会型",
                "hook": "前3秒钩子",
                "conflict": "冲突内容",
            })
            self.assertIsNotNone(obj["id"])
            self.assertEqual(obj["story_type"], "误会型")


class ScriptCRUDTest(DatabaseTestCase):
    """Test script CRUD operations."""

    def test_create_script(self):
        with get_db() as conn:
            project = crud.project_create(conn, {"name": "测试项目"})
            product = crud.product_create(conn, {
                "project_id": project["id"],
                "name": "测试商品",
                "category": "apparel_warmth",
            })
            idea = crud.story_idea_create(conn, {
                "product_id": product["id"],
                "title": "测试创意",
            })
            obj = crud.script_create(conn, {
                "story_idea_id": idea["id"],
                "version": 1,
                "title": "测试剧本",
                "content": "剧本内容...",
            })
            self.assertIsNotNone(obj["id"])
            self.assertEqual(obj["version"], 1)

    def test_script_version_history(self):
        with get_db() as conn:
            project = crud.project_create(conn, {"name": "测试项目"})
            product = crud.product_create(conn, {
                "project_id": project["id"],
                "name": "测试商品",
                "category": "other",
            })
            idea = crud.story_idea_create(conn, {"product_id": product["id"], "title": "创意"})
            s1 = crud.script_create(conn, {
                "story_idea_id": idea["id"], "version": 1,
                "title": "剧本v1", "content": "内容1",
            })
            s2 = crud.script_create(conn, {
                "story_idea_id": idea["id"], "version": 2,
                "title": "剧本v2", "content": "内容2",
            })
            scripts = crud.script_list(conn, story_idea_id=idea["id"])
            self.assertEqual(len(scripts), 2)


class StoryboardCRUDTest(DatabaseTestCase):
    """Test storyboard CRUD operations."""

    def test_create_storyboard(self):
        with get_db() as conn:
            project = crud.project_create(conn, {"name": "测试项目"})
            product = crud.product_create(conn, {
                "project_id": project["id"],
                "name": "测试商品",
                "category": "other",
            })
            idea = crud.story_idea_create(conn, {"product_id": product["id"], "title": "创意"})
            script = crud.script_create(conn, {
                "story_idea_id": idea["id"], "version": 1,
                "title": "剧本", "content": "内容",
            })
            obj = crud.storyboard_create(conn, {
                "script_id": script["id"],
                "shot_number": 1,
                "description": "镜头1",
                "image_prompt": "提示词1",
            })
            self.assertIsNotNone(obj["id"])
            self.assertEqual(obj["shot_number"], 1)


class AdvertisementCRUDTest(DatabaseTestCase):
    """Test advertisement CRUD operations."""

    def test_create_advertisement(self):
        with get_db() as conn:
            project = crud.project_create(conn, {"name": "测试项目"})
            obj = crud.advertisement_create(conn, {
                "project_id": project["id"],
                "version": 1,
                "title": "测试广告",
                "status": "draft",
            })
            self.assertIsNotNone(obj["id"])
            self.assertEqual(obj["status"], "draft")


class ComplianceReviewCRUDTest(DatabaseTestCase):
    """Test compliance review CRUD operations."""

    def test_create_compliance_review(self):
        with get_db() as conn:
            project = crud.project_create(conn, {"name": "测试项目"})
            ad = crud.advertisement_create(conn, {
                "project_id": project["id"], "version": 1, "title": "广告",
            })
            obj = crud.compliance_review_create(conn, {
                "advertisement_id": ad["id"],
                "reviewer_type": "agent",
                "ai_disclosure_required": True,
                "status": "pending",
            })
            self.assertIsNotNone(obj["id"])
            self.assertEqual(obj["status"], "pending")


class HealthEndpointTest(unittest.TestCase):
    """Test health endpoint via the HTTP server."""

    def test_health_endpoint(self):
        import app.api.server as server_mod
        # Just verify the server module loads and route table exists
        self.assertTrue(len(server_mod.ROUTES) > 0)
        health_routes = [r for r in server_mod.ROUTES if r[2] == "health"]
        self.assertEqual(len(health_routes), 1)


if __name__ == "__main__":
    unittest.main()
