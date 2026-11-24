"""AI Story Commerce — G5 人物与分镜管理测试套件"""

import sys
import os
import unittest
import json
import tempfile
import shutil

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "backend", "stdlib"))

from app.db.session import get_db, init_db, generate_id, now_iso
import app.crud.crud as crud
from app.character_management import (
    CharacterBible,
    CharacterRelationshipManager,
    ScriptCharacterAssociation,
    StoryboardGenerator,
    compute_sha256,
)


class CharacterBibleTest(unittest.TestCase):
    """测试虚拟人物圣经管理"""

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

    def test_create_character(self):
        with get_db() as conn:
            bible = CharacterBible()
            char = bible.create_character(conn, {
                "name": "阿强",
                "gender": "male",
                "age_range": "35-45",
                "personality": "爱面子、嘴硬、爱占小便宜",
                "is_core_ip": True,
            })
            self.assertIsNotNone(char["id"])
            self.assertEqual(char["name"], "阿强")
            self.assertEqual(char["gender"], "male")
            self.assertEqual(char["is_core_ip"], 1)

    def test_get_character_bible(self):
        with get_db() as conn:
            bible = CharacterBible()
            char = bible.create_character(conn, {
                "name": "测试人物",
                "gender": "female",
                "age_range": "25-35",
            })
            full_bible = bible.get_character_bible(conn, char["id"])
            self.assertIsNotNone(full_bible)
            self.assertEqual(full_bible["character"]["id"], char["id"])
            self.assertIn("assets", full_bible)
            self.assertIn("relationships", full_bible)

    def test_upload_and_verify_asset(self):
        with get_db() as conn:
            bible = CharacterBible()
            char = bible.create_character(conn, {
                "name": "资产测试人物",
                "gender": "male",
            })

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tmp.write(b"fake image data")
            tmp.close()

            try:
                asset = bible.upload_character_asset(
                    conn, char["id"], "face_reference", tmp.name,
                    description="面部参考图"
                )
                self.assertIsNotNone(asset["id"])
                self.assertEqual(asset["asset_type"], "face_reference")
                self.assertIsNotNone(asset["sha256"])
                self.assertEqual(asset["sha256"], compute_sha256(tmp.name))

                verification = bible.verify_asset_integrity(conn, char["id"], asset["id"])
                self.assertTrue(verification["verified"])
            finally:
                os.unlink(tmp.name)

    def test_check_required_assets(self):
        with get_db() as conn:
            bible = CharacterBible()
            char = bible.create_character(conn, {
                "name": "资产检查人物",
                "gender": "male",
            })

            check = bible.check_required_assets(conn, char["id"])
            self.assertFalse(check["complete"])
            self.assertEqual(len(check["missing"]), 5)

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tmp.write(b"face data")
            tmp.close()
            try:
                bible.upload_character_asset(conn, char["id"], "face_reference", tmp.name)
                check = bible.check_required_assets(conn, char["id"])
                self.assertIn("face_reference", check["present"])
                self.assertEqual(len(check["missing"]), 4)
            finally:
                os.unlink(tmp.name)


class CharacterRelationshipTest(unittest.TestCase):
    """测试人物关系管理"""

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

    def test_add_and_get_relationship(self):
        with get_db() as conn:
            bible = CharacterBible()
            char_a = bible.create_character(conn, {"name": "人物A", "gender": "male"})
            char_b = bible.create_character(conn, {"name": "人物B", "gender": "female"})

            mgr = CharacterRelationshipManager()
            rel = mgr.add_relationship(
                conn, char_a["id"], char_b["id"], "夫妻", "夫妻关系"
            )
            self.assertEqual(rel["relationship_type"], "夫妻")
            self.assertEqual(rel["description"], "夫妻关系")

            rels_a = mgr.get_relationships(conn, char_a["id"])
            self.assertEqual(len(rels_a), 1)
            self.assertEqual(rels_a[0]["relationship_type"], "夫妻")

            rels_b = mgr.get_relationships(conn, char_b["id"])
            self.assertEqual(len(rels_b), 1)


def _create_full_chain(conn):
    """创建项目-商品-创意-剧本的完整链条，返回 script_id."""
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
    return script


class ScriptCharacterAssociationTest(unittest.TestCase):
    """测试剧本与人物关联"""

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

    def test_associate_character_with_script(self):
        with get_db() as conn:
            bible = CharacterBible()
            char = bible.create_character(conn, {"name": "关联测试人物", "gender": "male"})
            script = _create_full_chain(conn)

            assoc = ScriptCharacterAssociation()
            result = assoc.associate_character_with_script(conn, script["id"], char["id"])
            self.assertEqual(result["script_id"], script["id"])
            self.assertEqual(result["character_id"], char["id"])

            chars = assoc.get_characters_for_script(conn, script["id"])
            self.assertEqual(len(chars), 1)
            self.assertEqual(chars[0]["id"], char["id"])

            scripts = assoc.get_scripts_for_character(conn, char["id"])
            self.assertEqual(len(scripts), 1)
            self.assertEqual(scripts[0]["id"], script["id"])

    def test_verify_cross_project_reuse(self):
        with get_db() as conn:
            bible = CharacterBible()
            char = bible.create_character(conn, {
                "name": "复用测试人物",
                "gender": "male",
                "is_core_ip": True,
            })
            script = _create_full_chain(conn)

            assoc = ScriptCharacterAssociation()
            assoc.associate_character_with_script(conn, script["id"], char["id"])

            verify = assoc.verify_cross_project_reuse(conn, char["id"])
            self.assertFalse(verify["reusable"])
            self.assertFalse(verify["bible_complete"])


class StoryboardGeneratorTest(unittest.TestCase):
    """测试分镜自动生成"""

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

    def test_generate_storyboards(self):
        with get_db() as conn:
            bible = CharacterBible()
            char = bible.create_character(conn, {"name": "分镜测试人物", "gender": "male"})
            script = _create_full_chain(conn)

            generator = StoryboardGenerator()
            storyboards = generator.generate_storyboards(conn, script["id"])
            self.assertGreaterEqual(len(storyboards), 7)

            shot_numbers = [sb["shot_number"] for sb in storyboards]
            self.assertEqual(shot_numbers, list(range(1, len(storyboards) + 1)))

            for sb in storyboards:
                self.assertIsNotNone(sb["image_prompt"])
                self.assertIsNotNone(sb["description"])

    def test_get_storyboards_for_script(self):
        with get_db() as conn:
            bible = CharacterBible()
            char = bible.create_character(conn, {"name": "人物", "gender": "male"})
            script = _create_full_chain(conn)

            generator = StoryboardGenerator()
            generator.generate_storyboards(conn, script["id"])

            retrieved = generator.get_storyboards_for_script(conn, script["id"])
            self.assertGreaterEqual(len(retrieved), 7)


class ComputeSHA256Test(unittest.TestCase):
    """测试 SHA256 计算"""

    def test_compute_sha256(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(b"test content for hash")
        tmp.close()
        try:
            h = compute_sha256(tmp.name)
            self.assertEqual(len(h), 64)
            self.assertTrue(all(c in "0123456789abcdef" for c in h))
        finally:
            os.unlink(tmp.name)


class CharacterReuseAcrossScriptsTest(unittest.TestCase):
    """测试同一人物在多个剧本中的复用"""

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

    def test_character_appears_in_multiple_scripts(self):
        with get_db() as conn:
            bible = CharacterBible()
            char = bible.create_character(conn, {
                "name": "阿强",
                "gender": "male",
                "is_core_ip": True,
            })
            project = crud.project_create(conn, {"name": "项目A"})

            for i in range(2):
                product = crud.product_create(conn, {
                    "project_id": project["id"],
                    "name": f"商品{i}",
                    "category": "other",
                })
                idea = crud.story_idea_create(conn, {
                    "product_id": product["id"],
                    "title": f"创意{i}",
                })
                script = crud.script_create(conn, {
                    "story_idea_id": idea["id"],
                    "version": 1,
                    "title": f"剧本{i}",
                    "content": f"内容{i}",
                })
                assoc = ScriptCharacterAssociation()
                assoc.associate_character_with_script(conn, script["id"], char["id"])

            scripts = crud.script_list(conn)
            self.assertEqual(len(scripts), 2)

            assoc = ScriptCharacterAssociation()
            char_scripts = assoc.get_scripts_for_character(conn, char["id"])
            self.assertEqual(len(char_scripts), 2)


if __name__ == "__main__":
    unittest.main()
