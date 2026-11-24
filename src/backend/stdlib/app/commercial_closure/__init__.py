"""AI Story Commerce — G8 商业闭环验证模块

对应立项方案 D22–D30 阶段：商业订单与闭环验收

实现：
1. 商家需求分析记录
2. 客户定制广告生产订单管理
3. 客户交付与验收流程
4. 广告数据追踪（对接 G7 性能指标）
5. 复盘分析（人物表现、剧情表现）
6. 投资决策支持（基于 30 天后决策规则）
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.db.session import get_db
import app.crud.crud as crud


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# 商家需求分析
# ---------------------------------------------------------------------------
class RequirementAnalysis:
    """商家需求分析记录

    记录商家对 AI 剧情广告的需求，包括商品、预算、投放目标、
    人物偏好、合规边界等，作为定制广告生产的输入。
    """

    def create_requirement(self, conn, customer_id: str,
                           project_id: Optional[str] = None,
                           product_name: Optional[str] = None,
                           budget_cny: Optional[float] = None,
                           target_audience: Optional[str] = None,
                           preferred_story_type: Optional[str] = None,
                           preferred_character: Optional[str] = None,
                           compliance_boundary: Optional[str] = None,
                           delivery_deadline: Optional[str] = None,
                           notes: Optional[str] = None) -> Dict[str, Any]:
        """创建商家需求分析记录"""
        customer = crud.customer_get(conn, customer_id)
        if not customer:
            raise ValueError(f"客户 {customer_id} 不存在")

        req_data = {
            "customer_id": customer_id,
            "project_id": project_id,
            "product_name": product_name,
            "budget_cny": budget_cny,
            "target_audience": target_audience,
            "preferred_story_type": preferred_story_type,
            "preferred_character": preferred_character,
            "compliance_boundary": compliance_boundary,
            "delivery_deadline": delivery_deadline,
            "notes": notes,
            "status": "pending",
            "created_at": now_iso(),
        }
        ts = now_iso()
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_requirement_analysis",
            "resource_type": "requirement_analysis",
            "resource_id": f"req_{customer_id}_{ts}",
            "details": json.dumps(req_data, ensure_ascii=False),
        })
        req_data["resource_id"] = f"req_{customer_id}_{ts}"
        return req_data

    def list_requirements(self, conn, customer_id: Optional[str] = None,
                          status: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出需求分析记录"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_requirement_analysis":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if customer_id and data.get("customer_id") != customer_id:
                continue
            if status and data.get("status") != status:
                continue
            results.append(data)
        return results

    def update_requirement_status(self, conn, resource_id: str,
                                  status: str) -> Optional[Dict[str, Any]]:
        """更新需求状态（pending/analyzed/quoted/accepted/rejected）"""
        logs = crud.audit_log_list(conn)
        for log in logs:
            if (log.get("action") == "create_requirement_analysis" and
                    log.get("resource_id") == resource_id):
                try:
                    data = json.loads(log.get("details", "{}"))
                except json.JSONDecodeError:
                    continue
                data["status"] = status
                data["updated_at"] = now_iso()
                crud.audit_log_update(conn, log["id"], {
                    "details": json.dumps(data, ensure_ascii=False),
                })
                return data
        return None


# ---------------------------------------------------------------------------
# 客户定制广告生产订单
# ---------------------------------------------------------------------------
class ProductionOrder:
    """客户定制广告生产订单管理

    将商家需求转化为可执行的生产订单，关联 G1–G6 的生产模块。
    订单状态：pending -> in_production -> review -> delivered -> accepted/rejected
    """

    ORDER_STATUSES = ["pending", "in_production", "review", "delivered", "accepted", "rejected"]

    def create_order(self, conn, customer_id: str,
                     requirement_resource_id: str,
                     ad_title: str,
                     ad_script_id: Optional[str] = None,
                     agreed_price_cny: Optional[float] = None,
                     delivery_deadline: Optional[str] = None) -> Dict[str, Any]:
        """创建生产订单"""
        customer = crud.customer_get(conn, customer_id)
        if not customer:
            raise ValueError(f"客户 {customer_id} 不存在")

        ts = now_iso()
        order_data = {
            "customer_id": customer_id,
            "requirement_resource_id": requirement_resource_id,
            "ad_title": ad_title,
            "ad_script_id": ad_script_id,
            "agreed_price_cny": agreed_price_cny,
            "delivery_deadline": delivery_deadline,
            "status": "pending",
            "delivered_at": None,
            "accepted_at": None,
            "created_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_production_order",
            "resource_type": "production_order",
            "resource_id": f"order_{customer_id}_{ts}",
            "details": json.dumps(order_data, ensure_ascii=False),
        })
        order_data["resource_id"] = f"order_{customer_id}_{ts}"
        return order_data

    def list_orders(self, conn, customer_id: Optional[str] = None,
                    status: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出生产订单"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_production_order":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if customer_id and data.get("customer_id") != customer_id:
                continue
            if status and data.get("status") != status:
                continue
            results.append(data)
        return results

    def update_order_status(self, conn, resource_id: str,
                            status: str) -> Optional[Dict[str, Any]]:
        """更新订单状态"""
        if status not in self.ORDER_STATUSES:
            raise ValueError(f"无效的订单状态：{status}")

        logs = crud.audit_log_list(conn)
        for log in logs:
            if (log.get("action") == "create_production_order" and
                    log.get("resource_id") == resource_id):
                try:
                    data = json.loads(log.get("details", "{}"))
                except json.JSONDecodeError:
                    continue
                data["status"] = status
                data["updated_at"] = now_iso()
                if status == "delivered":
                    data["delivered_at"] = now_iso()
                if status == "accepted":
                    data["accepted_at"] = now_iso()
                crud.audit_log_update(conn, log["id"], {
                    "details": json.dumps(data, ensure_ascii=False),
                })
                return data
        return None

    def get_order_by_resource_id(self, conn, resource_id: str) -> Optional[Dict[str, Any]]:
        """根据资源 ID 获取订单详情"""
        logs = crud.audit_log_list(conn)
        for log in logs:
            if (log.get("action") == "create_production_order" and
                    log.get("resource_id") == resource_id):
                try:
                    return json.loads(log.get("details", "{}"))
                except json.JSONDecodeError:
                    continue
        return None


# ---------------------------------------------------------------------------
# 客户交付与验收
# ---------------------------------------------------------------------------
class DeliveryAcceptance:
    """客户交付与验收流程

    记录广告成片交付给商家，商家验收结果，以及修改记录。
    """

    def record_delivery(self, conn, order_resource_id: str,
                        ad_file_path: str,
                        ad_sha256: str,
                        delivery_notes: Optional[str] = None) -> Dict[str, Any]:
        """记录交付"""
        order_mgr = ProductionOrder()
        order = order_mgr.get_order_by_resource_id(conn, order_resource_id)
        if not order:
            raise ValueError(f"订单 {order_resource_id} 不存在")

        ts = now_iso()
        delivery_data = {
            "order_resource_id": order_resource_id,
            "ad_file_path": ad_file_path,
            "ad_sha256": ad_sha256,
            "delivery_notes": delivery_notes,
            "delivered_at": ts,
            "acceptance_status": "pending",
            "revision_count": 0,
            "resource_id": f"delivery_{order_resource_id}_{ts}",
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "record_delivery",
            "resource_type": "delivery",
            "resource_id": delivery_data["resource_id"],
            "details": json.dumps(delivery_data, ensure_ascii=False),
        })
        order_mgr.update_order_status(conn, order_resource_id, "delivered")
        return delivery_data

    def record_acceptance(self, conn, delivery_resource_id: str,
                          accepted: bool,
                          acceptance_notes: Optional[str] = None,
                          revision_request: Optional[str] = None) -> Dict[str, Any]:
        """记录验收结果"""
        logs = crud.audit_log_list(conn)
        for log in logs:
            if (log.get("action") == "record_delivery" and
                    log.get("resource_id") == delivery_resource_id):
                try:
                    data = json.loads(log.get("details", "{}"))
                except json.JSONDecodeError:
                    continue
                if accepted:
                    data["acceptance_status"] = "accepted"
                    data["accepted_at"] = now_iso()
                    data["acceptance_notes"] = acceptance_notes
                    order_mgr = ProductionOrder()
                    order_mgr.update_order_status(conn, data["order_resource_id"], "accepted")
                else:
                    data["acceptance_status"] = "rejected"
                    data["rejection_notes"] = acceptance_notes
                    data["revision_request"] = revision_request
                    data["revision_count"] = data.get("revision_count", 0) + 1
                    data["rejected_at"] = now_iso()
                    order_mgr = ProductionOrder()
                    order_mgr.update_order_status(conn, data["order_resource_id"], "rejected")
                crud.audit_log_update(conn, log["id"], {
                    "details": json.dumps(data, ensure_ascii=False),
                })
                return data
        return None

    def list_deliveries(self, conn, order_resource_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出交付记录"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "record_delivery":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if order_resource_id and data.get("order_resource_id") != order_resource_id:
                continue
            results.append(data)
        return results


# ---------------------------------------------------------------------------
# 广告数据追踪（对接 G7 性能指标）
# ---------------------------------------------------------------------------
class AdPerformanceTracking:
    """广告数据追踪

    对接 G7 的 PerformanceDataManager，记录已发布广告的真实表现数据，
    用于客户交付后的效果复盘。
    """

    def __init__(self):
        from app.data_analysis import PerformanceDataManager, MetricsCalculator
        self.perf_mgr = PerformanceDataManager()
        self.calc = MetricsCalculator()

    def record_customer_ad_performance(self, conn, publishing_record_id: str,
                                       views: Optional[int] = None,
                                       completion_rate: Optional[float] = None,
                                       likes: Optional[int] = None,
                                       comments: Optional[int] = None,
                                       shares: Optional[int] = None,
                                       product_clicks: Optional[int] = None,
                                       orders: Optional[int] = None,
                                       cost_cny: Optional[float] = None) -> Dict[str, Any]:
        """录入客户广告的真实效果数据"""
        metric = self.perf_mgr.record_performance(
            conn, publishing_record_id,
            views=views, completion_rate=completion_rate,
            likes=likes, comments=comments, shares=shares,
            product_clicks=product_clicks, orders=orders, cost_cny=cost_cny,
        )
        return metric

    def get_customer_ad_summary(self, conn, advertisement_id: str) -> Dict[str, Any]:
        """获取客户广告的效果汇总"""
        records = crud.publishing_record_list(conn, advertisement_id=advertisement_id)
        all_metrics = []
        for pr in records:
            ms = crud.performance_metric_list(conn, publishing_record_id=pr["id"])
            for m in ms:
                m["_publishing_record_id"] = pr["id"]
                all_metrics.append(m)

        if not all_metrics:
            return {"advertisement_id": advertisement_id, "data_points": 0}

        total_views = sum(m.get("views") or 0 for m in all_metrics)
        total_clicks = sum(m.get("product_clicks") or 0 for m in all_metrics)
        total_orders = sum(m.get("orders") or 0 for m in all_metrics)
        total_cost = sum(m.get("cost_cny") or 0 for m in all_metrics)

        cpa = self.calc.calculate_cpa(total_cost, total_orders) if total_orders > 0 else None
        ctr = self.calc.calculate_ctr(total_views, total_clicks)
        cvr = self.calc.calculate_cvr(total_clicks, total_orders)

        return {
            "advertisement_id": advertisement_id,
            "total_views": total_views,
            "total_product_clicks": total_clicks,
            "total_orders": total_orders,
            "total_cost_cny": round(total_cost, 2),
            "ctr": ctr,
            "cvr": cvr,
            "cpa_cny": cpa,
            "data_points": len(all_metrics),
        }


# ---------------------------------------------------------------------------
# 复盘分析（人物表现、剧情表现）
# ---------------------------------------------------------------------------
class RetrospectiveAnalysis:
    """复盘分析

    分析核心人物（阿强）和不同剧情类型的表现，为下一阶段投资决策提供依据。
    """

    def analyze_character_performance(self, conn, character_id: str) -> Dict[str, Any]:
        """分析人物表现：该人物参与的广告效果汇总"""
        scripts = crud.script_list(conn)
        character_scripts = []
        for s in scripts:
            with get_db() as c:
                rows = c.execute(
                    """SELECT sc.character_id FROM script_characters sc
                       WHERE sc.script_id = ? AND sc.character_id = ?""",
                    (s["id"], character_id),
                ).fetchall()
                if rows:
                    character_scripts.append(s)

        ad_performances = []
        for s in character_scripts:
            with get_db() as c:
                rows = c.execute(
                    """SELECT a.* FROM advertisements a
                       WHERE a.script_id = ?""",
                    (s["id"],),
                ).fetchall()
                for row in rows:
                    ad_id = row["id"]
                    perf = self._get_ad_performance(conn, ad_id)
                    ad_performances.append({
                        "advertisement_id": ad_id,
                        "advertisement_title": row.get("title"),
                        "performance": perf,
                    })

        return {
            "character_id": character_id,
            "total_ads": len(ad_performances),
            "ads": ad_performances,
        }

    def analyze_story_type_performance(self, conn) -> Dict[str, Any]:
        """分析不同剧情类型的表现"""
        ads = crud.advertisement_list(conn)

        story_type_results = {}
        for ad in ads:
            script_id = ad.get("script_id")
            if not script_id:
                continue
            script = crud.script_get(conn, script_id)
            if not script:
                continue
            story_idea_id = script.get("story_idea_id")
            if not story_idea_id:
                continue
            idea = crud.story_idea_get(conn, story_idea_id)
            if not idea:
                continue
            story_type = idea.get("story_type", "未知")

            perf = self._get_ad_performance(conn, ad["id"])
            if story_type not in story_type_results:
                story_type_results[story_type] = []
            story_type_results[story_type].append({
                "advertisement_id": ad["id"],
                "advertisement_title": ad.get("title"),
                "performance": perf,
            })

        type_summary = {}
        for stype, ads_list in story_type_results.items():
            total_views = sum(a["performance"].get("total_views", 0) for a in ads_list)
            total_orders = sum(a["performance"].get("total_orders", 0) for a in ads_list)
            total_cost = sum(a["performance"].get("total_cost_cny", 0) for a in ads_list)
            cpa = None
            if total_orders > 0:
                cpa = round(total_cost / total_orders, 2)
            type_summary[stype] = {
                "ad_count": len(ads_list),
                "total_views": total_views,
                "total_orders": total_orders,
                "total_cost_cny": round(total_cost, 2),
                "cpa_cny": cpa,
            }

        return {
            "story_type_summary": type_summary,
            "best_story_type": max(type_summary.items(),
                                   key=lambda x: x[1].get("total_orders", 0))[0]
                                   if type_summary else None,
        }

    def _get_ad_performance(self, conn, advertisement_id: str) -> Dict[str, Any]:
        """获取单个广告的效果数据（简化版）"""
        records = crud.publishing_record_list(conn, advertisement_id=advertisement_id)
        all_metrics = []
        for pr in records:
            ms = crud.performance_metric_list(conn, publishing_record_id=pr["id"])
            all_metrics.extend(ms)

        if not all_metrics:
            return {"data_points": 0}

        return {
            "total_views": sum(m.get("views") or 0 for m in all_metrics),
            "total_orders": sum(m.get("orders") or 0 for m in all_metrics),
            "total_cost_cny": round(sum(m.get("cost_cny") or 0 for m in all_metrics), 2),
            "data_points": len(all_metrics),
        }


# ---------------------------------------------------------------------------
# 投资决策支持（基于 30 天后决策规则）
# ---------------------------------------------------------------------------
class InvestmentDecision:
    """投资决策支持

    基于立项方案第九部分的 30 天后决策规则：
    - 有付费客户 -> 继续扩大服务
    - 有兴趣无订单 -> 调整商业方案
    - 视频好但无转化 -> 调整剧情与商品结合方式
    - 没有有效需求 -> 暂停扩张
    """

    def evaluate_30_day_result(self, conn,
                               commercial_metrics: Dict[str, Any],
                               content_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """评估 30 天商业验证结果，给出投资决策建议

        输入：
        - commercial_metrics: G7 报告中的商业指标
        - content_metrics: G7 报告中的内容指标
        """
        paid_orders = commercial_metrics.get("paid_trial_orders", 0)
        has_interest = commercial_metrics.get("customer_count", 0) > 0
        total_ads = content_metrics.get("total_advertisements", 0)

        decision_tree = {
            "paid_orders": paid_orders,
            "has_interest": has_interest,
            "total_ads": total_ads,
        }

        if paid_orders >= 1:
            decision = {
                "branch": "continue_expand",
                "action": "继续扩大服务",
                "reason": "有付费客户，商业验证通过",
                "recommendations": [
                    "优化报价，提高生产效率",
                    "发展核心人物 IP",
                    "扩大商家开发范围",
                ],
            }
        elif has_interest and paid_orders == 0:
            decision = {
                "branch": "adjust_business",
                "action": "调整商业方案",
                "reason": "有兴趣无订单，检查客户需求、价格、样片和销售流程",
                "recommendations": [
                    "重新审视客户痛点和定价",
                    "优化样片质量和展示方式",
                    "改进销售话术和流程",
                ],
            }
        elif total_ads > 0 and paid_orders == 0:
            decision = {
                "branch": "adjust_creative",
                "action": "调整剧情与商品结合方式",
                "reason": "视频好但无转化，检查购买理由、商品展示和受众匹配",
                "recommendations": [
                    "强化商品植入自然度",
                    "优化购买理由表达",
                    "匹配目标受众喜好",
                ],
            }
        else:
            decision = {
                "branch": "pause_expand",
                "action": "暂停扩张",
                "reason": "没有有效需求，重新评估行业、客户和产品定位",
                "recommendations": [
                    "重新评估目标行业和客户群体",
                    "调整产品定位",
                    "暂停扩大投入",
                ],
            }

        return {
            "evaluated_at": now_iso(),
            "decision_tree": decision_tree,
            "decision": decision,
            "overall_conclusion": decision["action"],
        }

    def generate_investment_report(self, conn,
                                   g7_report: Dict[str, Any]) -> Dict[str, Any]:
        """生成完整的投资决策报告"""
        commercial = g7_report.get("commercial_metrics", {})
        content = g7_report.get("content_metrics", {})

        evaluation = self.evaluate_30_day_result(conn, commercial, content)

        return {
            "report_type": "30_day_investment_decision",
            "generated_at": now_iso(),
            "commercial_metrics": commercial,
            "content_metrics": content,
            "evaluation": evaluation,
            "next_stage_authorization": evaluation["decision"]["branch"] == "continue_expand",
        }


__all__ = [
    "RequirementAnalysis",
    "ProductionOrder",
    "DeliveryAcceptance",
    "AdPerformanceTracking",
    "RetrospectiveAnalysis",
    "InvestmentDecision",
    "now_iso",
]
