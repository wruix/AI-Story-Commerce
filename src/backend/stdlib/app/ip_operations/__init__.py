"""AI Story Commerce — G10 虚拟人物 IP 运营模块

对应立项方案商业战略第二阶段：发展数字人IP公司

围绕核心人物“阿强”构建 IP 运营体系，实现：

1. 人物IP资产升级与一致性管理：形象、声音、性格固化
2. IP内容矩阵与账号多平台运营管理：内容矩阵、多平台账号运营
3. 粉丝运营与社区互动管理：粉丝画像、互动数据、留存分析
4. 人物IP商业变现管理：品牌合作、授权、周边、商业代言
5. 人物IP数据看板与运营指标：粉丝增长、互动率、IP商业价值
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.db.session import get_db
import app.crud.crud as crud


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# 1. 人物IP资产升级与一致性管理
# ---------------------------------------------------------------------------
class CharacterIPAsset:
    """虚拟人物IP资产管理

    确保同一人物在不同内容平台、不同制作批次中保持形象、声音、
    性格的一致性，实现人物IP的可复用、可资产化。
    """

    ASSET_CATEGORIES = [
        "face_reference",      # 面部参考图
        "expression_sheet",    # 表情参考图
        "pose_sheet",          # 姿态参考图
        "outfit_reference",    # 服装参考图
        "voice_reference",     # 声音参考
        "personality_bible",   # 性格与行为逻辑圣经
        "worldview_bible",     # 世界观圣经
        "voiceprint_model",    # 声纹模型
        "3d_model",            # 3D建模
    ]

    def register_asset(self, conn, character_name: str,
                       asset_category: str,
                       file_path: str,
                       asset_version: str = "v1.0",
                       description: Optional[str] = None,
                       usage_scope: Optional[str] = None,
                       commercial_rights: Optional[str] = None) -> Dict[str, Any]:
        """注册人物IP资产"""
        if asset_category not in self.ASSET_CATEGORIES:
            raise ValueError(f"无效的资产类别：{asset_category}")

        ts = now_iso()
        asset_data = {
            "character_name": character_name,
            "asset_category": asset_category,
            "file_path": file_path,
            "asset_version": asset_version,
            "description": description,
            "usage_scope": usage_scope,
            "commercial_rights": commercial_rights,
            "status": "active",
            "created_at": ts,
            "updated_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "register_ip_asset",
            "resource_type": "ip_asset",
            "resource_id": f"asset_{character_name}_{asset_category}_{ts}",
            "details": json.dumps(asset_data, ensure_ascii=False),
        })
        asset_data["asset_id"] = f"asset_{character_name}_{asset_category}_{ts}"
        return asset_data

    def list_assets(self, conn, character_name: Optional[str] = None,
                    category: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出IP资产"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "register_ip_asset":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if character_name and data.get("character_name") != character_name:
                continue
            if category and data.get("asset_category") != category:
                continue
            results.append(data)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results

    def verify_asset_consistency(self, conn, character_name: str,
                                 category: str) -> Dict[str, Any]:
        """验证人物资产一致性：确保同一人物同一类别只使用标准化资产"""
        assets = self.list_assets(conn, character_name=character_name, category=category)
        versions = set(a.get("asset_version") for a in assets)
        return {
            "character_name": character_name,
            "category": category,
            "asset_count": len(assets),
            "version_count": len(versions),
            "versions": sorted(list(versions)),
            "is_consistent": len(versions) <= 1,
        }


# ---------------------------------------------------------------------------
# 2. IP内容矩阵与账号多平台运营管理
# ---------------------------------------------------------------------------
class IPContentMatrix:
    """IP内容矩阵管理

    管理虚拟人物IP的内容发布矩阵，包括内容类型、主题、风格、
    发布频率、平台分发等。
    """

    CONTENT_TYPES = [
        "短视频", "连续剧情", "直播切片", "表情包", "图文", "长视频",
    ]
    CONTENT_STYLES = [
        "喜剧", "反转", "悬疑", "温情", "励志", "荒诞", "对抗",
    ]

    def create_content_item(self, conn, character_name: str,
                            platform: str,
                            content_type: str,
                            title: str,
                            style: Optional[str] = None,
                            theme: Optional[str] = None,
                            scheduled_time: Optional[str] = None,
                            status: str = "planned") -> Dict[str, Any]:
        """创建IP内容条目"""
        if content_type not in self.CONTENT_TYPES:
            raise ValueError(f"无效的内容类型：{content_type}")
        if style and style not in self.CONTENT_STYLES:
            raise ValueError(f"无效的内容风格：{style}")

        ts = now_iso()
        content_data = {
            "character_name": character_name,
            "platform": platform,
            "content_type": content_type,
            "title": title,
            "style": style,
            "theme": theme,
            "scheduled_time": scheduled_time,
            "status": status,
            "actual_publish_time": None,
            "created_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_ip_content",
            "resource_type": "ip_content",
            "resource_id": f"content_{character_name}_{platform}_{ts}",
            "details": json.dumps(content_data, ensure_ascii=False),
        })
        content_data["content_id"] = f"content_{character_name}_{platform}_{ts}"
        return content_data

    def list_content(self, conn, character_name: Optional[str] = None,
                     platform: Optional[str] = None,
                     status: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出IP内容"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_ip_content":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if character_name and data.get("character_name") != character_name:
                continue
            if platform and data.get("platform") != platform:
                continue
            if status and data.get("status") != status:
                continue
            results.append(data)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results

    def mark_published(self, conn, content_id: str,
                       publish_time: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """标记内容已发布"""
        ts = publish_time or now_iso()
        logs = crud.audit_log_list(conn)
        for log in logs:
            if (log.get("action") == "create_ip_content" and
                    log.get("resource_id") == content_id):
                try:
                    data = json.loads(log.get("details", "{}"))
                except json.JSONDecodeError:
                    continue
                data["status"] = "published"
                data["actual_publish_time"] = ts
                crud.audit_log_update(conn, log["id"], {
                    "details": json.dumps(data, ensure_ascii=False),
                })
                return data
        return None


class MultiPlatformAccount:
    """IP账号多平台运营管理

    管理虚拟人物IP在不同社交平台的账号，包括抖音、B站、微博、小红书等。
    """

    PLATFORMS = [
        "douyin", "bilibili", "weibo", "xiaohongshu", "kuaishou", "video_account",
    ]

    def register_account(self, conn, character_name: str,
                         platform: str,
                         account_name: str,
                         account_url: Optional[str] = None,
                         bio: Optional[str] = None,
                         is_verified: bool = False) -> Dict[str, Any]:
        """注册IP账号"""
        if platform not in self.PLATFORMS:
            raise ValueError(f"不支持的平台：{platform}")

        ts = now_iso()
        account_data = {
            "character_name": character_name,
            "platform": platform,
            "account_name": account_name,
            "account_url": account_url,
            "bio": bio,
            "is_verified": is_verified,
            "status": "active",
            "created_at": ts,
            "updated_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "register_ip_account",
            "resource_type": "ip_account",
            "resource_id": f"account_{character_name}_{platform}_{ts}",
            "details": json.dumps(account_data, ensure_ascii=False),
        })
        account_data["account_id"] = f"account_{character_name}_{platform}_{ts}"
        return account_data

    def list_accounts(self, conn, character_name: Optional[str] = None,
                      platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出IP账号"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "register_ip_account":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if character_name and data.get("character_name") != character_name:
                continue
            if platform and data.get("platform") != platform:
                continue
            results.append(data)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results


# ---------------------------------------------------------------------------
# 3. 粉丝运营与社区互动管理
# ---------------------------------------------------------------------------
class FanProfile:
    """粉丝画像管理

    记录虚拟人物IP粉丝的基本信息、偏好、互动历史等。
    """

    def create_fan_profile(self, conn, character_name: str,
                           fan_id: str,
                           platform: str,
                           fan_name: Optional[str] = None,
                           age_group: Optional[str] = None,
                           gender: Optional[str] = None,
                           location: Optional[str] = None,
                           interest_tags: Optional[List[str]] = None,
                           follow_time: Optional[str] = None) -> Dict[str, Any]:
        """创建粉丝画像"""
        ts = now_iso()
        profile_data = {
            "character_name": character_name,
            "fan_id": fan_id,
            "platform": platform,
            "fan_name": fan_name,
            "age_group": age_group,
            "gender": gender,
            "location": location,
            "interest_tags": json.dumps(interest_tags or [], ensure_ascii=False),
            "follow_time": follow_time,
            "created_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_fan_profile",
            "resource_type": "fan_profile",
            "resource_id": f"fan_{character_name}_{fan_id}_{ts}",
            "details": json.dumps(profile_data, ensure_ascii=False),
        })
        return profile_data

    def list_fans(self, conn, character_name: Optional[str] = None,
                  platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出粉丝"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_fan_profile":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if character_name and data.get("character_name") != character_name:
                continue
            if platform and data.get("platform") != platform:
                continue
            results.append(data)
        return results


class InteractionRecord:
    """粉丝互动记录

    记录粉丝与IP内容的互动数据，包括点赞、评论、分享、私信等。
    """

    INTERACTION_TYPES = [
        "like", "comment", "share", "follow", "unfollow", "private_message",
    ]

    def record_interaction(self, conn, character_name: str,
                           platform: str,
                           fan_id: str,
                           interaction_type: str,
                           content_id: Optional[str] = None,
                           content: Optional[str] = None,
                           sentiment: Optional[str] = None) -> Dict[str, Any]:
        """记录粉丝互动"""
        if interaction_type not in self.INTERACTION_TYPES:
            raise ValueError(f"无效的互动类型：{interaction_type}")

        ts = now_iso()
        record_data = {
            "character_name": character_name,
            "platform": platform,
            "fan_id": fan_id,
            "interaction_type": interaction_type,
            "content_id": content_id,
            "content": content,
            "sentiment": sentiment,
            "interaction_time": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "record_fan_interaction",
            "resource_type": "fan_interaction",
            "resource_id": f"interaction_{character_name}_{fan_id}_{ts}",
            "details": json.dumps(record_data, ensure_ascii=False),
        })
        record_data["interaction_id"] = f"interaction_{character_name}_{fan_id}_{ts}"
        return record_data

    def list_interactions(self, conn, character_name: Optional[str] = None,
                          platform: Optional[str] = None,
                          interaction_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出互动记录"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "record_fan_interaction":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if character_name and data.get("character_name") != character_name:
                continue
            if platform and data.get("platform") != platform:
                continue
            if interaction_type and data.get("interaction_type") != interaction_type:
                continue
            results.append(data)
        results.sort(key=lambda x: x.get("interaction_time", ""), reverse=True)
        return results


class FanRetention:
    """粉丝留存分析

    分析粉丝的留存率、流失率、活跃度等。
    """

    def calculate_retention_rate(self, conn, character_name: str,
                                 period_start: str,
                                 period_end: str) -> Dict[str, Any]:
        """计算粉丝留存率"""
        fans = []
        logs = crud.audit_log_list(conn)
        for log in logs:
            if log.get("action") == "create_fan_profile":
                try:
                    data = json.loads(log.get("details", "{}"))
                    if data.get("character_name") == character_name:
                        fans.append(data)
                except json.JSONDecodeError:
                    continue

        total_fans = len(fans)
        retained = sum(1 for f in fans
                       if period_start <= f.get("follow_time", "") <= period_end)
        retention_rate = round(retained / total_fans * 100, 2) if total_fans > 0 else 0.0

        return {
            "character_name": character_name,
            "period_start": period_start,
            "period_end": period_end,
            "total_fans": total_fans,
            "retained_fans": retained,
            "retention_rate_percent": retention_rate,
        }


# ---------------------------------------------------------------------------
# 4. 人物IP商业变现管理
# ---------------------------------------------------------------------------
class BrandCollaboration:
    """品牌合作管理

    管理虚拟人物IP与品牌的商业合作，包括合作意向、合同、履行、结算。
    """

    COLLABORATION_STATUSES = [
        "意向", "洽谈", "已签约", "执行中", "已完成", "已终止",
    ]

    def create_collaboration(self, conn, character_name: str,
                             brand_name: str,
                             collaboration_type: str,
                             contract_amount_cny: float,
                             start_date: str,
                             end_date: str,
                             deliverables: Optional[str] = None,
                             status: str = "意向") -> Dict[str, Any]:
        """创建品牌合作"""
        if status not in self.COLLABORATION_STATUSES:
            raise ValueError(f"无效的合作状态：{status}")

        ts = now_iso()
        collab_data = {
            "character_name": character_name,
            "brand_name": brand_name,
            "collaboration_type": collaboration_type,
            "contract_amount_cny": contract_amount_cny,
            "start_date": start_date,
            "end_date": end_date,
            "deliverables": deliverables,
            "status": status,
            "created_at": ts,
            "updated_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_brand_collaboration",
            "resource_type": "brand_collaboration",
            "resource_id": f"collab_{character_name}_{brand_name}_{ts}",
            "details": json.dumps(collab_data, ensure_ascii=False),
        })
        collab_data["collab_id"] = f"collab_{character_name}_{brand_name}_{ts}"
        return collab_data

    def list_collaborations(self, conn, character_name: Optional[str] = None,
                            status: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出品牌合作"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_brand_collaboration":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if character_name and data.get("character_name") != character_name:
                continue
            if status and data.get("status") != status:
                continue
            results.append(data)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results


class LicensingManagement:
    """IP授权管理

    管理虚拟人物IP的授权业务，包括授权方、授权范围、授权费、授权期限。
    """

    def create_license(self, conn, character_name: str,
                       licensee: str,
                       license_scope: str,
                       license_fee_cny: float,
                       start_date: str,
                       end_date: str,
                       territory: Optional[str] = None) -> Dict[str, Any]:
        """创建IP授权"""
        ts = now_iso()
        license_data = {
            "character_name": character_name,
            "licensee": licensee,
            "license_scope": license_scope,
            "license_fee_cny": license_fee_cny,
            "start_date": start_date,
            "end_date": end_date,
            "territory": territory,
            "status": "active",
            "created_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_ip_license",
            "resource_type": "ip_license",
            "resource_id": f"license_{character_name}_{licensee}_{ts}",
            "details": json.dumps(license_data, ensure_ascii=False),
        })
        license_data["license_id"] = f"license_{character_name}_{licensee}_{ts}"
        return license_data

    def list_licenses(self, conn, character_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出IP授权"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_ip_license":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if character_name and data.get("character_name") != character_name:
                continue
            results.append(data)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results


class MerchandiseManagement:
    """IP周边管理

    管理虚拟人物IP周边产品的开发、销售、库存。
    """

    def create_merchandise(self, conn, character_name: str,
                           product_name: str,
                           category: str,
                           price_cny: float,
                           cost_cny: float,
                           inventory: int,
                           description: Optional[str] = None) -> Dict[str, Any]:
        """创建周边产品"""
        ts = now_iso()
        merch_data = {
            "character_name": character_name,
            "product_name": product_name,
            "category": category,
            "price_cny": price_cny,
            "cost_cny": cost_cny,
            "inventory": inventory,
            "description": description,
            "status": "onsale",
            "created_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_merchandise",
            "resource_type": "merchandise",
            "resource_id": f"merch_{character_name}_{product_name}_{ts}",
            "details": json.dumps(merch_data, ensure_ascii=False),
        })
        merch_data["merch_id"] = f"merch_{character_name}_{product_name}_{ts}"
        return merch_data

    def list_merchandise(self, conn, character_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出周边产品"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_merchandise":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if character_name and data.get("character_name") != character_name:
                continue
            results.append(data)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results


# ---------------------------------------------------------------------------
# 5. 人物IP数据看板与运营指标
# ---------------------------------------------------------------------------
class IPMetricsDashboard:
    """IP数据看板与运营指标

    计算粉丝增长、互动率、IP商业价值等关键指标。
    """

    def calculate_fan_growth(self, conn, character_name: str,
                             period_start: str,
                             period_end: str) -> Dict[str, Any]:
        """计算粉丝增长"""
        fans = []
        logs = crud.audit_log_list(conn)
        for log in logs:
            if log.get("action") == "create_fan_profile":
                try:
                    data = json.loads(log.get("details", "{}"))
                    if data.get("character_name") == character_name:
                        fans.append(data)
                except json.JSONDecodeError:
                    continue

        total = len(fans)
        in_period = sum(1 for f in fans
                        if period_start <= f.get("follow_time", "") <= period_end)

        return {
            "character_name": character_name,
            "period_start": period_start,
            "period_end": period_end,
            "total_fans": total,
            "new_fans_in_period": in_period,
        }

    def calculate_interaction_rate(self, conn, character_name: str,
                                   platform: Optional[str] = None) -> Dict[str, Any]:
        """计算互动率：总互动数 / 总粉丝数"""
        interactions = []
        logs = crud.audit_log_list(conn)
        for log in logs:
            if log.get("action") == "record_fan_interaction":
                try:
                    data = json.loads(log.get("details", "{}"))
                    if data.get("character_name") == character_name:
                        if platform is None or data.get("platform") == platform:
                            interactions.append(data)
                except json.JSONDecodeError:
                    continue

        fans = []
        for log in logs:
            if log.get("action") == "create_fan_profile":
                try:
                    data = json.loads(log.get("details", "{}"))
                    if data.get("character_name") == character_name:
                        if platform is None or data.get("platform") == platform:
                            fans.append(data)
                except json.JSONDecodeError:
                    continue

        total_interactions = len(interactions)
        total_fans = len(fans)
        interaction_rate = round(total_interactions / total_fans * 100, 2) if total_fans > 0 else 0.0

        return {
            "character_name": character_name,
            "platform": platform,
            "total_interactions": total_interactions,
            "total_fans": total_fans,
            "interaction_rate_percent": interaction_rate,
        }

    def calculate_ip_commercial_value(self, conn, character_name: str) -> Dict[str, Any]:
        """计算IP商业价值：基于品牌合作、授权、周边收入"""
        collabs = []
        licenses = []
        merch = []
        logs = crud.audit_log_list(conn)
        for log in logs:
            action = log.get("action")
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if data.get("character_name") != character_name:
                continue
            if action == "create_brand_collaboration":
                collabs.append(data)
            elif action == "create_ip_license":
                licenses.append(data)
            elif action == "create_merchandise":
                merch.append(data)

        collab_revenue = sum(c.get("contract_amount_cny", 0) for c in collabs
                             if c.get("status") in ("已签约", "执行中", "已完成"))
        license_revenue = sum(l.get("license_fee_cny", 0) for l in licenses)
        merch_revenue = sum(m.get("price_cny", 0) * m.get("inventory", 0) for m in merch)

        total_value = collab_revenue + license_revenue + merch_revenue

        return {
            "character_name": character_name,
            "brand_collaboration_revenue_cny": round(collab_revenue, 2),
            "licensing_revenue_cny": round(license_revenue, 2),
            "merchandise_potential_revenue_cny": round(merch_revenue, 2),
            "total_commercial_value_cny": round(total_value, 2),
            "collab_count": len(collabs),
            "license_count": len(licenses),
            "merchandise_count": len(merch),
        }

    def generate_ip_dashboard(self, conn, character_name: str) -> Dict[str, Any]:
        """生成IP运营数据看板"""
        fan_growth = self.calculate_fan_growth(conn, character_name,
                                               "2026-01-01", now_iso()[:10])
        interaction = self.calculate_interaction_rate(conn, character_name)
        commercial = self.calculate_ip_commercial_value(conn, character_name)

        return {
            "character_name": character_name,
            "generated_at": now_iso(),
            "fan_growth": fan_growth,
            "interaction_rate": interaction,
            "commercial_value": commercial,
        }


__all__ = [
    "CharacterIPAsset",
    "IPContentMatrix",
    "MultiPlatformAccount",
    "FanProfile",
    "InteractionRecord",
    "FanRetention",
    "BrandCollaboration",
    "LicensingManagement",
    "MerchandiseManagement",
    "IPMetricsDashboard",
    "now_iso",
]
