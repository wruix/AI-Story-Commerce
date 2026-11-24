"""AI Story Commerce — 虚拟人物圣经管理模块

实现人物固定档案管理，确保同一人物在不同广告项目中
重复调用同一套人物资料，保持人物一致性。

核心资产：
1. 面部参考图
2. 正面、侧面、全身图
3. 年龄、身材、五官描述
4. 服装规范
5. 声音参考
6. 语言习惯
7. 性格与行为逻辑
8. 人物关系
9. 世界观
10. 商业合作边界
"""

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pathlib import Path

from app.db.session import get_db
import app.crud.crud as crud

CHARACTER_ASSETS_DIR = "data/character_assets"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def compute_sha256(file_path: str) -> str:
    """计算文件 SHA256 哈希值。"""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


class CharacterBible:
    """虚拟人物圣经 — 人物固定档案

    每个角色必须有固定的：
    1. 面部参考图
    2. 正面、侧面、全身图
    3. 年龄、身材和五官描述
    4. 服装规范
    5. 声音参考
    6. 语言习惯
    7. 性格与行为逻辑
    8. 人物关系
    9. 世界观
    10. 商业合作边界
    """

    REQUIRED_ASSET_TYPES = [
        "face_reference",     # 面部参考图
        "front_view",         # 正面图
        "side_view",          # 侧面图
        "full_body",          # 全身图
        "voice_reference",    # 声音参考
    ]

    OPTIONAL_ASSET_TYPES = [
        "outfit_reference",   # 服装规范图
        "expression_sheet",   # 表情参考图
        "pose_sheet",         # 姿态参考图
    ]

    def __init__(self):
        self.assets_root = Path(CHARACTER_ASSETS_DIR)
        self.assets_root.mkdir(parents=True, exist_ok=True)

    def create_character(self, conn, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建虚拟人物并建立人物圣经。

        必填字段：name, gender
        可选字段：age_range, background, personality, catchphrases,
                 worldview, commercial_boundary, voice_reference_url
        """
        if not character_data.get("name"):
            raise ValueError("人物姓名为必填项")
        if not character_data.get("gender"):
            raise ValueError("人物性别为必填项")

        db_character = crud.character_create(conn, character_data)
        return db_character

    def get_character_bible(self, conn, character_id: str) -> Dict[str, Any]:
        """获取完整的人物圣经，包括基础信息和所有资产。"""
        character = crud.character_get(conn, character_id)
        if not character:
            return None

        assets = self.list_character_assets(conn, character_id)
        rel_mgr = CharacterRelationshipManager()
        relationships = rel_mgr.get_relationships(conn, character_id)

        bible = {
            "character": character,
            "assets": assets,
            "relationships": relationships,
            "bible_version": 1,
            "generated_at": now_iso(),
        }
        return bible

    def update_character_bible(self, conn, character_id: str,
                               updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新人物圣经信息。"""
        character = crud.character_get(conn, character_id)
        if not character:
            return None

        updated = crud.character_update(conn, character_id, updates)
        return updated

    def upload_character_asset(self, conn, character_id: str,
                               asset_type: str, file_path: str,
                               description: Optional[str] = None) -> Dict[str, Any]:
        """上传人物参考资产，计算 SHA256 校验值。

        资产类型：face_reference, front_view, side_view, full_body,
                 voice_reference, outfit_reference, expression_sheet, pose_sheet
        """
        character = crud.character_get(conn, character_id)
        if not character:
            raise ValueError(f"人物 {character_id} 不存在")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"资产文件不存在：{file_path}")

        sha256 = compute_sha256(file_path)
        file_size = os.path.getsize(file_path)

        char_asset_dir = self.assets_root / character_id
        char_asset_dir.mkdir(parents=True, exist_ok=True)

        file_name = os.path.basename(file_path)
        dest_path = char_asset_dir / file_name
        shutil.copy2(file_path, dest_path)

        asset_data = {
            "character_id": character_id,
            "asset_type": asset_type,
            "file_path": str(dest_path),
            "sha256": sha256,
            "file_size_bytes": file_size,
            "description": description or "",
        }
        asset = crud.character_asset_create(conn, asset_data)
        return asset

    def verify_asset_integrity(self, conn, character_id: str,
                               asset_id: str) -> Dict[str, Any]:
        """验证人物资产文件的完整性（SHA256 校验）。"""
        asset = crud.character_asset_get(conn, asset_id)
        if not asset:
            return {"verified": False, "error": "资产不存在"}

        if asset.get("character_id") != character_id:
            return {"verified": False, "error": "资产不属于指定人物"}

        file_path = asset["file_path"]
        if not os.path.exists(file_path):
            return {"verified": False, "error": "文件不存在"}

        current_sha256 = compute_sha256(file_path)
        verified = current_sha256 == asset["sha256"]

        return {
            "verified": verified,
            "asset_id": asset_id,
            "file_path": file_path,
            "recorded_sha256": asset["sha256"],
            "current_sha256": current_sha256,
        }

    def list_character_assets(self, conn, character_id: str) -> List[Dict[str, Any]]:
        """列出人物的所有参考资产。"""
        return crud.character_asset_list(conn, character_id=character_id)

    def check_required_assets(self, conn, character_id: str) -> Dict[str, Any]:
        """检查人物是否拥有所有必填资产类型。"""
        assets = self.list_character_assets(conn, character_id)
        existing_types = {a["asset_type"] for a in assets}

        missing = [t for t in self.REQUIRED_ASSET_TYPES if t not in existing_types]
        present = [t for t in self.REQUIRED_ASSET_TYPES if t in existing_types]

        return {
            "character_id": character_id,
            "complete": len(missing) == 0,
            "present": present,
            "missing": missing,
            "required_count": len(self.REQUIRED_ASSET_TYPES),
            "present_count": len(present),
        }


class CharacterRelationshipManager:
    """人物关系管理器

    维护人物之间的关系，如家庭、邻里、职场关系等。
    """

    RELATIONSHIP_TYPES = [
        "夫妻", "父母子女", "婆媳", "邻居", "同事",
        "上下级", "朋友", "对手", "陌生人",
    ]

    def __init__(self):
        pass

    def add_relationship(self, conn, from_character_id: str,
                         to_character_id: str,
                         relationship_type: str,
                         description: Optional[str] = None) -> Dict[str, Any]:
        """添加人物关系。"""
        if relationship_type not in self.RELATIONSHIP_TYPES:
            raise ValueError(f"不支持的关系类型：{relationship_type}")

        relationship_data = {
            "from_character_id": from_character_id,
            "to_character_id": to_character_id,
            "relationship_type": relationship_type,
            "description": description or "",
            "created_at": now_iso(),
        }

        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "add_character_relationship",
            "resource_type": "character_relationship",
            "resource_id": f"{from_character_id}_{to_character_id}",
            "details": json.dumps(relationship_data, ensure_ascii=False),
        })

        return relationship_data

    def get_relationships(self, conn, character_id: str) -> List[Dict[str, Any]]:
        """获取人物的所有关系。"""
        logs = crud.audit_log_list(conn)
        relationships = []
        for log in logs:
            if log.get("action") == "add_character_relationship":
                try:
                    data = json.loads(log.get("details", "{}"))
                    if data.get("from_character_id") == character_id or data.get("to_character_id") == character_id:
                        relationships.append(data)
                except json.JSONDecodeError:
                    continue
        return relationships

    def get_character_relationships(self, conn, character_id: str) -> List[Dict[str, Any]]:
        """获取人物关系（别名方法）。"""
        return self.get_relationships(conn, character_id)


class ScriptCharacterAssociation:
    """剧本与人物关联管理（多对多）

    一个剧本可关联多个角色，一个角色可在多个剧本中出现。
    """

    def __init__(self):
        pass

    def associate_character_with_script(self, conn, script_id: str,
                                        character_id: str) -> Dict[str, Any]:
        """将角色关联到剧本。"""
        script = crud.script_get(conn, script_id)
        if not script:
            raise ValueError(f"剧本 {script_id} 不存在")

        character = crud.character_get(conn, character_id)
        if not character:
            raise ValueError(f"人物 {character_id} 不存在")

        conn.execute(
            "INSERT OR IGNORE INTO script_characters (script_id, character_id) VALUES (?, ?)",
            (script_id, character_id),
        )
        conn.commit()

        return {
            "script_id": script_id,
            "character_id": character_id,
            "associated_at": now_iso(),
        }

    def get_characters_for_script(self, conn, script_id: str) -> List[Dict[str, Any]]:
        """获取剧本关联的所有角色。"""
        script = crud.script_get(conn, script_id)
        if not script:
            return []

        with get_db() as c:
            rows = c.execute(
                """SELECT c.* FROM characters c
                   JOIN script_characters sc ON c.id = sc.character_id
                   WHERE sc.script_id = ?""",
                (script_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_scripts_for_character(self, conn, character_id: str) -> List[Dict[str, Any]]:
        """获取角色出现的所有剧本。"""
        character = crud.character_get(conn, character_id)
        if not character:
            return []

        with get_db() as c:
            rows = c.execute(
                """SELECT s.* FROM scripts s
                   JOIN script_characters sc ON s.id = sc.script_id
                   WHERE sc.character_id = ?""",
                (character_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def verify_cross_project_reuse(self, conn, character_id: str) -> Dict[str, Any]:
        """验证人物是否可以在不同项目中重复使用。"""
        character = crud.character_get(conn, character_id)
        if not character:
            return {"reusable": False, "error": "人物不存在"}

        bible_mgr = CharacterBible()
        asset_check = bible_mgr.check_required_assets(conn, character_id)

        scripts = self.get_scripts_for_character(conn, character_id)

        return {
            "character_id": character_id,
            "character_name": character["name"],
            "is_core_ip": bool(character.get("is_core_ip")),
            "bible_complete": asset_check["complete"],
            "missing_assets": asset_check["missing"],
            "scripts_appeared": len(scripts),
            "script_ids": [s["id"] for s in scripts],
            "reusable": asset_check["complete"] and bool(character.get("is_core_ip")),
        }


class StoryboardGenerator:
    """分镜自动生成器

    将剧本转换为分镜表，每个镜头关联画面提示词、对白、音效。
    """

    def generate_storyboards(self, conn, script_id: str) -> List[Dict[str, Any]]:
        """根据剧本自动生成分镜表。

        输入：script_id
        输出：分镜列表，每个分镜包含镜头号、画面描述、画面提示词、对白、音效、时长
        """
        script = crud.script_get(conn, script_id)
        if not script:
            raise ValueError(f"剧本 {script_id} 不存在")

        script_content = script.get("content", "")
        script_title = script.get("title", "")

        storyboards = []

        storyboards.append(self._create_storyboard(
            conn, script_id, 1,
            description="前3秒钩子：吸引注意力的开场画面",
            image_prompt=f"15秒广告开场，{script_title}，视觉冲击力强的画面",
            dialogue="",
            sound_effect="背景音乐起始",
            duration_seconds=3.0,
        ))

        storyboards.append(self._create_storyboard(
            conn, script_id, 2,
            description="第3-7秒冲突：人物产生分歧或遇到问题",
            image_prompt=f"冲突场景，人物表情生动，{script_title}",
            dialogue="冲突对白",
            sound_effect="环境音效",
            duration_seconds=2.0,
        ))
        storyboards.append(self._create_storyboard(
            conn, script_id, 3,
            description="冲突升级：矛盾达到高潮",
            image_prompt=f"紧张氛围，特写人物表情，{script_title}",
            dialogue="激烈对白",
            sound_effect="音效强化",
            duration_seconds=2.0,
        ))

        storyboards.append(self._create_storyboard(
            conn, script_id, 4,
            description="第7-11秒反转：出人意料的转折",
            image_prompt=f"反转场景，出人意料的画面，{script_title}",
            dialogue="反转对白",
            sound_effect="反转音效",
            duration_seconds=2.0,
        ))
        storyboards.append(self._create_storyboard(
            conn, script_id, 5,
            description="反转后的结果：问题解决或新局面",
            image_prompt=f"反转后画面，{script_title}",
            dialogue="结果对白",
            sound_effect="轻快音效",
            duration_seconds=2.0,
        ))

        storyboards.append(self._create_storyboard(
            conn, script_id, 6,
            description="第11-13秒：商品登场，展示卖点",
            image_prompt=f"商品特写，{script_title}商品展示",
            dialogue="商品介绍对白",
            sound_effect="产品音效",
            duration_seconds=2.0,
        ))
        storyboards.append(self._create_storyboard(
            conn, script_id, 7,
            description="第13-15秒：购买理由与行动号召",
            image_prompt=f"购买场景，{script_title}行动号召",
            dialogue="购买理由",
            sound_effect="行动号召音效",
            duration_seconds=2.0,
        ))

        return storyboards

    def _create_storyboard(self, conn, script_id: str, shot_number: int,
                           description: str, image_prompt: str,
                           dialogue: str, sound_effect: str,
                           duration_seconds: float) -> Dict[str, Any]:
        """创建单个分镜并保存到数据库。"""
        storyboard_data = {
            "script_id": script_id,
            "shot_number": shot_number,
            "description": description,
            "image_prompt": image_prompt,
            "dialogue": dialogue,
            "sound_effect": sound_effect,
            "duration_seconds": duration_seconds,
        }
        storyboard = crud.storyboard_create(conn, storyboard_data)
        return storyboard

    def get_storyboards_for_script(self, conn, script_id: str) -> List[Dict[str, Any]]:
        """获取剧本的所有分镜。"""
        return crud.storyboard_list(conn, script_id=script_id)


__all__ = [
    "CharacterBible",
    "CharacterRelationshipManager",
    "ScriptCharacterAssociation",
    "StoryboardGenerator",
    "compute_sha256",
]
