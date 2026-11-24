"""AI Story Commerce — 视频生产与合规审核模块

实现：
1. 视频生产任务管理（创建、状态跟踪、输入输出）
2. 素材手动上传与管理
3. 图像/视频/配音生成适配器接口
4. FFmpeg 后期处理
5. 成片版本管理
6. 人工审核流程（合规审核硬门槛）
7. AI 生成内容标识记录
8. 发布记录与效果数据
"""

import json
import os
import shutil
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pathlib import Path

from app.db.session import get_db
import app.crud.crud as crud

MATERIALS_DIR = "data/materials"
OUTPUTS_DIR = "data/outputs"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def compute_file_sha256(file_path: str) -> str:
    """计算文件 SHA256 哈希值"""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


class VideoProductionManager:
    """视频生产任务管理器"""

    def __init__(self):
        self.materials_root = Path(MATERIALS_DIR)
        self.outputs_root = Path(OUTPUTS_DIR)
        self.materials_root.mkdir(parents=True, exist_ok=True)
        self.outputs_root.mkdir(parents=True, exist_ok=True)

    def create_production_task(self, conn, storyboard_id: Optional[str],
                               task_type: str, input_data: Optional[str] = None) -> Dict[str, Any]:
        """创建视频生产任务

        task_type: image_gen, video_gen, voice, edit
        """
        storyboard = None
        if storyboard_id:
            storyboard = crud.storyboard_get(conn, storyboard_id)
            if not storyboard:
                raise ValueError(f"分镜 {storyboard_id} 不存在")

        task_data = {
            "storyboard_id": storyboard_id,
            "task_type": task_type,
            "status": "pending",
            "input_data": input_data,
        }
        task = crud.production_task_create(conn, task_data)
        return task

    def update_task_status(self, conn, task_id: str, status: str,
                           output_data: Optional[str] = None,
                           error_message: Optional[str] = None) -> Dict[str, Any]:
        """更新任务状态"""
        task = crud.production_task_get(conn, task_id)
        if not task:
            raise ValueError(f"任务 {task_id} 不存在")

        update_data = {"status": status}
        if output_data is not None:
            update_data["output_data"] = output_data
        if error_message is not None:
            update_data["error_message"] = error_message

        from datetime import datetime, timezone
        if status == "in_progress" and not task.get("started_at"):
            update_data["started_at"] = now_iso()
        if status in ("completed", "failed"):
            update_data["completed_at"] = now_iso()

        updated = crud.production_task_update(conn, task_id, update_data)
        return updated

    def list_tasks(self, conn, storyboard_id: Optional[str] = None,
                   status: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出演生产任务"""
        tasks = crud.production_task_list(conn, storyboard_id=storyboard_id)
        if status:
            tasks = [t for t in tasks if t.get("status") == status]
        return tasks


class MaterialManager:
    """素材手动上传与管理"""

    def __init__(self):
        self.materials_root = Path(MATERIALS_DIR)
        self.materials_root.mkdir(parents=True, exist_ok=True)

    def upload_material(self, conn, storyboard_id: Optional[str],
                        production_task_id: Optional[str],
                        media_type: str, file_path: str,
                        ai_generated: bool = False,
                        ai_disclosure: bool = False,
                        description: Optional[str] = None) -> Dict[str, Any]:
        """上传素材文件，计算 SHA256 校验值

        media_type: image, video, audio
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"素材文件不存在: {file_path}")

        sha256 = compute_file_sha256(file_path)
        file_size = os.path.getsize(file_path)

        # 复制到素材目录
        mat_dir = self.materials_root / "uploads"
        mat_dir.mkdir(parents=True, exist_ok=True)
        file_name = os.path.basename(file_path)
        dest_path = mat_dir / file_name
        shutil.copy2(file_path, dest_path)

        # 获取视频/音频时长和尺寸（如果 ffprobe 可用）
        duration = None
        width = None
        height = None
        try:
            from app.video_production.ffmpeg import FFmpegProcessor
            ffmpeg = FFmpegProcessor()
            info = ffmpeg.get_video_info(str(dest_path))
            if info and "format" in info:
                try:
                    duration = float(info["format"].get("duration", 0))
                except (ValueError, TypeError):
                    pass
            if info and "streams" in info:
                for stream in info["streams"]:
                    if stream.get("codec_type") == "video":
                        width = stream.get("width")
                        height = stream.get("height")
                        break
        except Exception:
            pass

        asset_data = {
            "storyboard_id": storyboard_id,
            "production_task_id": production_task_id,
            "media_type": media_type,
            "file_path": str(dest_path),
            "sha256": sha256,
            "file_size_bytes": file_size,
            "duration_seconds": duration,
            "width": width,
            "height": height,
            "ai_generated": 1 if ai_generated else 0,
            "ai_disclosure": 1 if ai_disclosure else 0,
        }
        asset = crud.media_asset_create(conn, asset_data)
        return asset

    def list_materials(self, conn, storyboard_id: Optional[str] = None,
                       media_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出素材"""
        assets = crud.media_asset_list(conn, storyboard_id=storyboard_id)
        if media_type:
            assets = [a for a in assets if a.get("media_type") == media_type]
        return assets

    def verify_material_integrity(self, conn, asset_id: str) -> Dict[str, Any]:
        """验证素材文件完整性"""
        asset = crud.media_asset_get(conn, asset_id)
        if not asset:
            return {"verified": False, "error": "素材不存在"}

        file_path = asset["file_path"]
        if not os.path.exists(file_path):
            return {"verified": False, "error": "文件不存在"}

        current_sha256 = compute_file_sha256(file_path)
        verified = current_sha256 == asset["sha256"]

        return {
            "verified": verified,
            "asset_id": asset_id,
            "file_path": file_path,
            "recorded_sha256": asset["sha256"],
            "current_sha256": current_sha256,
        }


class ComplianceReviewManager:
    """合规审核管理器 — 发布前的硬门槛

    所有审核项目必须全部通过，才能允许发布。
    """

    REQUIRED_CHECKS = [
        "ai_disclosure_confirmed",
        "product_authenticity",
        "fictional_experience_check",
        "portrait_authorization",
        "voice_clone_authorization",
        "music_license",
        "trademark_check",
        "ad_content_compliance",
    ]

    def create_review(self, conn, advertisement_id: str,
                      reviewer_type: str = "agent") -> Dict[str, Any]:
        """创建合规审核记录"""
        review_data = {
            "advertisement_id": advertisement_id,
            "reviewer_type": reviewer_type,
            "ai_disclosure_required": 1,
            "ai_disclosure_confirmed": 0,
            "status": "pending",
        }
        review = crud.compliance_review_create(conn, review_data)
        return review

    def update_review_item(self, conn, review_id: str,
                           check_item: str, passed: bool) -> Dict[str, Any]:
        """更新单个审核项目"""
        review = crud.compliance_review_get(conn, review_id)
        if not review:
            raise ValueError(f"审核 {review_id} 不存在")

        update_data = {check_item: 1 if passed else 0}
        updated = crud.compliance_review_update(conn, review_id, update_data)
        return updated

    def complete_review(self, conn, review_id: str,
                        reviewer_remarks: Optional[str] = None) -> Dict[str, Any]:
        """完成审核，判定是否通过

        所有 REQUIRED_CHECKS 必须全部为 True，审核才能通过。
        """
        review = crud.compliance_review_get(conn, review_id)
        if not review:
            raise ValueError(f"审核 {review_id} 不存在")

        # 检查所有必填项
        all_passed = True
        failed_items = []
        for item in self.REQUIRED_CHECKS:
            if not review.get(item):
                all_passed = False
                failed_items.append(item)

        status = "passed" if all_passed else "failed"
        update_data = {
            "status": status,
            "reviewed_at": now_iso(),
        }
        if reviewer_remarks:
            update_data["remarks"] = reviewer_remarks

        updated = crud.compliance_review_update(conn, review_id, update_data)

        return {
            "review_id": review_id,
            "status": status,
            "all_passed": all_passed,
            "failed_items": failed_items,
            "can_publish": all_passed,
            "review": updated,
        }

    def can_publish(self, conn, advertisement_id: str) -> Dict[str, Any]:
        """检查广告是否可以发布（所有审核必须通过）"""
        reviews = crud.compliance_review_list(conn, advertisement_id=advertisement_id)
        if not reviews:
            return {"can_publish": False, "reason": "无审核记录"}

        latest = reviews[0]  # 假设按创建时间倒序，最新的在前
        if latest.get("status") != "passed":
            return {
                "can_publish": False,
                "reason": f"审核未通过，状态：{latest.get('status')}",
                "review_id": latest.get("id"),
            }

        return {"can_publish": True, "review_id": latest.get("id")}

    def check_ai_disclosure(self, conn, advertisement_id: str) -> Dict[str, Any]:
        """检查 AI 生成内容标识状态"""
        review = crud.compliance_review_get(conn, advertisement_id) if False else None
        reviews = crud.compliance_review_list(conn, advertisement_id=advertisement_id)
        if not reviews:
            return {"ai_disclosure_required": True, "ai_disclosure_confirmed": False}

        latest = reviews[0]
        return {
            "ai_disclosure_required": bool(latest.get("ai_disclosure_required")),
            "ai_disclosure_confirmed": bool(latest.get("ai_disclosure_confirmed")),
            "review_id": latest.get("id"),
        }


class AdvertisementVersionManager:
    """成片版本管理

    保留广告版本历史，不覆盖旧版本。
    """

    def create_advertisement(self, conn, project_id: str, title: str,
                             script_id: Optional[str] = None,
                             file_path: Optional[str] = None,
                             ai_disclosure: bool = False) -> Dict[str, Any]:
        """创建广告成片（自动版本号）"""
        # 获取该项目下的最大版本号
        existing = crud.advertisement_list(conn, project_id=project_id)
        max_version = 0
        for ad in existing:
            v = ad.get("version", 0)
            if v > max_version:
                max_version = v

        ad_data = {
            "project_id": project_id,
            "script_id": script_id,
            "version": max_version + 1,
            "title": title,
            "file_path": file_path,
            "status": "draft",
            "is_current": 1,
            "ai_disclosure": 1 if ai_disclosure else 0,
        }
        ad = crud.advertisement_create(conn, ad_data)

        # 将旧版本标记为非当前
        if len(existing) > 0:
            for old_ad in existing:
                if old_ad["id"] != ad["id"] and old_ad.get("is_current"):
                    crud.advertisement_update(conn, old_ad["id"], {"is_current": 0})

        return ad

    def get_current_advertisement(self, conn, project_id: str) -> Optional[Dict[str, Any]]:
        """获取项目的当前版本广告"""
        ads = crud.advertisement_list(conn, project_id=project_id)
        for ad in ads:
            if ad.get("is_current"):
                return ad
        return None

    def get_all_versions(self, conn, project_id: str) -> List[Dict[str, Any]]:
        """获取项目的所有广告版本"""
        return crud.advertisement_list(conn, project_id=project_id)


class PublishingManager:
    """发布记录与 AI 标识声明管理"""

    def create_publishing_record(self, conn, advertisement_id: str,
                                 platform: str = "douyin",
                                 account_name: Optional[str] = None,
                                 publish_url: Optional[str] = None,
                                 ai_disclosure_posted: bool = False) -> Dict[str, Any]:
        """创建发布记录"""
        record_data = {
            "advertisement_id": advertisement_id,
            "platform": platform,
            "account_name": account_name,
            "publish_url": publish_url,
            "ai_disclosure_posted": 1 if ai_disclosure_posted else 0,
        }
        record = crud.publishing_record_create(conn, record_data)
        return record

    def list_publishing_records(self, conn, advertisement_id: str) -> List[Dict[str, Any]]:
        """列出发布记录"""
        return crud.publishing_record_list(conn, advertisement_id=advertisement_id)

    def verify_ai_disclosure_posted(self, conn, record_id: str) -> Dict[str, Any]:
        """验证发布时是否声明了 AI 生成内容"""
        record = crud.publishing_record_get(conn, record_id)
        if not record:
            return {"posted": False, "error": "发布记录不存在"}

        return {
            "record_id": record_id,
            "ai_disclosure_posted": bool(record.get("ai_disclosure_posted")),
            "platform": record.get("platform"),
            "publish_url": record.get("publish_url"),
        }


__all__ = [
    "VideoProductionManager",
    "MaterialManager",
    "ComplianceReviewManager",
    "AdvertisementVersionManager",
    "PublishingManager",
    "compute_file_sha256",
    "now_iso",
]
