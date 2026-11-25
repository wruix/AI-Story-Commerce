"""AI Story Commerce — G9 商业化扩张模块

对应立项方案商业战略第一阶段：先做AI剧情广告服务公司

实现：
1. 商家客户关系管理（CRM）：商家画像、联系记录、商机跟踪
2. 商业化定价与报价系统：服务产品、报价模板、合同管理
3. 样片与作品集管理：商业展示样片、案例库、转化跟踪
4. 核心人物“阿强”IP运营启动：人物账号、内容发布计划、粉丝数据
5. 商业化运营指标仪表板：获客成本、客单价、复购率、ROI
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.db.session import get_db
import app.crud.crud as crud


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# 1. 商家客户关系管理（CRM）
# ---------------------------------------------------------------------------
class CustomerProfile:
    """商家客户画像管理

    记录商家的基本信息、行业类别、经营规模、合作偏好、合作历史等。
    """

    CUSTOMER_CATEGORIES = [
        "中小品牌", "电商经营者", "实体商家", "服务商", "其他",
    ]
    CUSTOMER_TIERS = [
        "潜在客户", "初次合作", "重复客户", "战略合作",
    ]

    def create_customer_profile(self, conn, customer_id: str,
                                category: str,
                                industry: Optional[str] = None,
                                business_scale: Optional[str] = None,
                                annual_revenue_cny: Optional[float] = None,
                                preferred_categories: Optional[List[str]] = None,
                                compliance_preference: Optional[str] = None,
                                notes: Optional[str] = None) -> Dict[str, Any]:
        """创建或更新商家画像"""
        customer = crud.customer_get(conn, customer_id)
        if not customer:
            raise ValueError(f"客户 {customer_id} 不存在")

        if category not in self.CUSTOMER_CATEGORIES:
            raise ValueError(f"无效的商家类别：{category}")

        profile_data = {
            "customer_id": customer_id,
            "category": category,
            "industry": industry,
            "business_scale": business_scale,
            "annual_revenue_cny": annual_revenue_cny,
            "preferred_categories": json.dumps(preferred_categories or [], ensure_ascii=False),
            "compliance_preference": compliance_preference,
            "notes": notes,
            "updated_at": now_iso(),
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_customer_profile",
            "resource_type": "customer_profile",
            "resource_id": f"profile_{customer_id}",
            "details": json.dumps(profile_data, ensure_ascii=False),
        })
        return profile_data

    def get_customer_profile(self, conn, customer_id: str) -> Optional[Dict[str, Any]]:
        """获取商家画像"""
        logs = crud.audit_log_list(conn)
        for log in reversed(logs):
            if (log.get("action") == "create_customer_profile" and
                    log.get("resource_id") == f"profile_{customer_id}"):
                try:
                    return json.loads(log.get("details", "{}"))
                except json.JSONDecodeError:
                    continue
        return None


class ContactRecord:
    """商家联系记录

    记录与商家的每一次沟通，包括时间、渠道、内容、结果、后续行动。
    """

    CONTACT_CHANNELS = [
        "电话", "微信", "抖音私信", "邮件", "面对面", "其他",
    ]
    CONTACT_OUTCOMES = [
        "待跟进", "有意向", "已报价", "已签约", "已拒绝", "失联",
    ]

    def create_contact_record(self, conn, customer_id: str,
                              contact_time: str,
                              channel: str,
                              content: str,
                              outcome: str,
                              next_action: Optional[str] = None,
                              next_action_time: Optional[str] = None,
                              notes: Optional[str] = None) -> Dict[str, Any]:
        """创建联系记录"""
        customer = crud.customer_get(conn, customer_id)
        if not customer:
            raise ValueError(f"客户 {customer_id} 不存在")

        if channel not in self.CONTACT_CHANNELS:
            raise ValueError(f"无效的联系渠道：{channel}")
        if outcome not in self.CONTACT_OUTCOMES:
            raise ValueError(f"无效的联系结果：{outcome}")

        ts = now_iso()
        record_data = {
            "customer_id": customer_id,
            "contact_time": contact_time,
            "channel": channel,
            "content": content,
            "outcome": outcome,
            "next_action": next_action,
            "next_action_time": next_action_time,
            "notes": notes,
            "created_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_contact_record",
            "resource_type": "contact_record",
            "resource_id": f"contact_{customer_id}_{ts}",
            "details": json.dumps(record_data, ensure_ascii=False),
        })
        return record_data

    def list_contact_records(self, conn, customer_id: str) -> List[Dict[str, Any]]:
        """列出客户的所有联系记录"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_contact_record":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if data.get("customer_id") != customer_id:
                continue
            results.append(data)
        results.sort(key=lambda x: x.get("contact_time", ""), reverse=True)
        return results


class SalesOpportunity:
    """商机跟踪

    跟踪从商家初次接触到签约的完整商机漏斗。
    """

    OPPORTUNITY_STAGES = [
        "初次接触", "需求分析", "方案报价", "合同谈判", "已签约", "已失单",
    ]

    def create_opportunity(self, conn, customer_id: str,
                           stage: str,
                           estimated_value_cny: Optional[float] = None,
                           expected_close_date: Optional[str] = None,
                           source: Optional[str] = None,
                           notes: Optional[str] = None) -> Dict[str, Any]:
        """创建商机"""
        customer = crud.customer_get(conn, customer_id)
        if not customer:
            raise ValueError(f"客户 {customer_id} 不存在")

        if stage not in self.OPPORTUNITY_STAGES:
            raise ValueError(f"无效的商机阶段：{stage}")

        ts = now_iso()
        opp_data = {
            "customer_id": customer_id,
            "stage": stage,
            "estimated_value_cny": estimated_value_cny,
            "expected_close_date": expected_close_date,
            "source": source,
            "notes": notes,
            "created_at": ts,
            "updated_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_opportunity",
            "resource_type": "opportunity",
            "resource_id": f"opp_{customer_id}_{ts}",
            "details": json.dumps(opp_data, ensure_ascii=False),
        })
        opp_data["opportunity_id"] = f"opp_{customer_id}_{ts}"
        return opp_data

    def update_opportunity_stage(self, conn, opportunity_id: str,
                                 stage: str) -> Optional[Dict[str, Any]]:
        """更新商机阶段"""
        if stage not in self.OPPORTUNITY_STAGES:
            raise ValueError(f"无效的商机阶段：{stage}")

        logs = crud.audit_log_list(conn)
        for log in logs:
            if (log.get("action") == "create_opportunity" and
                    log.get("resource_id") == opportunity_id):
                try:
                    data = json.loads(log.get("details", "{}"))
                except json.JSONDecodeError:
                    continue
                data["stage"] = stage
                data["updated_at"] = now_iso()
                crud.audit_log_update(conn, log["id"], {
                    "details": json.dumps(data, ensure_ascii=False),
                })
                return data
        return None

    def list_opportunities(self, conn, customer_id: Optional[str] = None,
                           stage: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出商机"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_opportunity":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if customer_id and data.get("customer_id") != customer_id:
                continue
            if stage and data.get("stage") != stage:
                continue
            results.append(data)
        return results


# ---------------------------------------------------------------------------
# 2. 商业化定价与报价系统
# ---------------------------------------------------------------------------
class ServiceProduct:
    """服务产品管理

    定义AI剧情广告服务的标准产品和报价。
    """

    SERVICE_PRODUCTS = [
        {"name": "创意试单", "description": "3个创意＋1条成片", "price_range": "¥1,500–3,000"},
        {"name": "标准广告", "description": "5条剧情广告", "price_range": "¥5,000–8,000"},
        {"name": "系列广告", "description": "10条剧情广告＋人物设计", "price_range": "¥12,000–20,000"},
    ]

    def list_service_products(self) -> List[Dict[str, Any]]:
        """列出所有标准服务产品"""
        return self.SERVICE_PRODUCTS

    def create_quote(self, conn, customer_id: str,
                     product_name: str,
                     quoted_price_cny: float,
                     ad_count: int,
                     revision_count: int,
                     delivery_deadline: str,
                     validity_period_days: int = 7,
                     notes: Optional[str] = None) -> Dict[str, Any]:
        """创建商业报价"""
        customer = crud.customer_get(conn, customer_id)
        if not customer:
            raise ValueError(f"客户 {customer_id} 不存在")

        ts = now_iso()
        quote_data = {
            "customer_id": customer_id,
            "product_name": product_name,
            "quoted_price_cny": quoted_price_cny,
            "ad_count": ad_count,
            "revision_count": revision_count,
            "delivery_deadline": delivery_deadline,
            "validity_period_days": validity_period_days,
            "status": "pending",
            "notes": notes,
            "created_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_quote",
            "resource_type": "quote",
            "resource_id": f"quote_{customer_id}_{ts}",
            "details": json.dumps(quote_data, ensure_ascii=False),
        })
        quote_data["quote_id"] = f"quote_{customer_id}_{ts}"
        return quote_data

    def list_quotes(self, conn, customer_id: Optional[str] = None,
                    status: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出报价"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_quote":
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


class ContractManagement:
    """合同管理

    管理与商家的广告制作合同，包括合同条款、签署状态、付款状态。
    """

    CONTRACT_STATUSES = ["草稿", "待签署", "已签署", "履行中", "已完成", "已终止"]
    PAYMENT_STATUSES = ["未付款", "部分付款", "已付款", "已退款"]

    def create_contract(self, conn, customer_id: str,
                        quote_id: str,
                        contract_amount_cny: float,
                        payment_terms: str,
                        ad_delivery_count: int,
                        contract_start_date: str,
                        contract_end_date: str,
                        terms_and_conditions: Optional[str] = None) -> Dict[str, Any]:
        """创建合同"""
        customer = crud.customer_get(conn, customer_id)
        if not customer:
            raise ValueError(f"客户 {customer_id} 不存在")

        ts = now_iso()
        contract_data = {
            "customer_id": customer_id,
            "quote_id": quote_id,
            "contract_amount_cny": contract_amount_cny,
            "payment_terms": payment_terms,
            "ad_delivery_count": ad_delivery_count,
            "contract_start_date": contract_start_date,
            "contract_end_date": contract_end_date,
            "terms_and_conditions": terms_and_conditions,
            "status": "草稿",
            "payment_status": "未付款",
            "created_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_contract",
            "resource_type": "contract",
            "resource_id": f"contract_{customer_id}_{ts}",
            "details": json.dumps(contract_data, ensure_ascii=False),
        })
        contract_data["contract_id"] = f"contract_{customer_id}_{ts}"
        return contract_data

    def update_contract_status(self, conn, contract_id: str,
                               status: str,
                               payment_status: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """更新合同状态"""
        if status not in self.CONTRACT_STATUSES:
            raise ValueError(f"无效的合同状态：{status}")
        if payment_status and payment_status not in self.PAYMENT_STATUSES:
            raise ValueError(f"无效的付款状态：{payment_status}")

        logs = crud.audit_log_list(conn)
        for log in logs:
            if (log.get("action") == "create_contract" and
                    log.get("resource_id") == contract_id):
                try:
                    data = json.loads(log.get("details", "{}"))
                except json.JSONDecodeError:
                    continue
                data["status"] = status
                if payment_status:
                    data["payment_status"] = payment_status
                data["updated_at"] = now_iso()
                crud.audit_log_update(conn, log["id"], {
                    "details": json.dumps(data, ensure_ascii=False),
                })
                return data
        return None

    def list_contracts(self, conn, customer_id: Optional[str] = None,
                       status: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出合同"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_contract":
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


# ---------------------------------------------------------------------------
# 3. 样片与作品集管理
# ---------------------------------------------------------------------------
class SampleAd:
    """样片与作品集管理

    管理用于商业展示的样片广告，包括案例库和转化跟踪。
    """

    def create_sample_ad(self, conn, ad_title: str,
                         ad_file_path: str,
                         ad_sha256: str,
                         product_category: str,
                         industry: str,
                         story_type: str,
                         character_name: Optional[str] = None,
                         views: Optional[int] = None,
                         likes: Optional[int] = None,
                         comments: Optional[int] = None,
                         shares: Optional[int] = None,
                         product_clicks: Optional[int] = None,
                         orders: Optional[int] = None,
                         cost_cny: Optional[float] = None,
                         is_featured: bool = False,
                         notes: Optional[str] = None) -> Dict[str, Any]:
        """创建样片作品集条目"""
        ts = now_iso()
        sample_data = {
            "ad_title": ad_title,
            "ad_file_path": ad_file_path,
            "ad_sha256": ad_sha256,
            "product_category": product_category,
            "industry": industry,
            "story_type": story_type,
            "character_name": character_name,
            "views": views or 0,
            "likes": likes or 0,
            "comments": comments or 0,
            "shares": shares or 0,
            "product_clicks": product_clicks or 0,
            "orders": orders or 0,
            "cost_cny": cost_cny or 0,
            "is_featured": is_featured,
            "notes": notes,
            "created_at": ts,
            "updated_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_sample_ad",
            "resource_type": "sample_ad",
            "resource_id": f"sample_{ts}",
            "details": json.dumps(sample_data, ensure_ascii=False),
        })
        sample_data["sample_id"] = f"sample_{ts}"
        return sample_data

    def list_sample_ads(self, conn, featured_only: bool = False,
                        category: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出样片作品集"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_sample_ad":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if featured_only and not data.get("is_featured"):
                continue
            if category and data.get("product_category") != category:
                continue
            results.append(data)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results

    def update_sample_metrics(self, conn, sample_id: str,
                              views: Optional[int] = None,
                              likes: Optional[int] = None,
                              comments: Optional[int] = None,
                              shares: Optional[int] = None,
                              product_clicks: Optional[int] = None,
                              orders: Optional[int] = None,
                              cost_cny: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """更新样片效果数据"""
        logs = crud.audit_log_list(conn)
        for log in logs:
            if (log.get("action") == "create_sample_ad" and
                    log.get("resource_id") == sample_id):
                try:
                    data = json.loads(log.get("details", "{}"))
                except json.JSONDecodeError:
                    continue
                if views is not None:
                    data["views"] = views
                if likes is not None:
                    data["likes"] = likes
                if comments is not None:
                    data["comments"] = comments
                if shares is not None:
                    data["shares"] = shares
                if product_clicks is not None:
                    data["product_clicks"] = product_clicks
                if orders is not None:
                    data["orders"] = orders
                if cost_cny is not None:
                    data["cost_cny"] = cost_cny
                data["updated_at"] = now_iso()
                crud.audit_log_update(conn, log["id"], {
                    "details": json.dumps(data, ensure_ascii=False),
                })
                return data
        return None


# ---------------------------------------------------------------------------
# 4. 核心人物“阿强”IP运营启动
# ---------------------------------------------------------------------------
class CharacterIPAccount:
    """核心人物“阿强”IP运营管理

    管理虚拟人物IP的账号、内容发布计划、粉丝数据。
    """

    def create_ip_account(self, conn, character_name: str,
                          platform: str,
                          account_name: str,
                          account_url: Optional[str] = None,
                          follower_count: int = 0,
                          total_views: int = 0,
                          total_likes: int = 0,
                          bio: Optional[str] = None,
                          is_active: bool = True) -> Dict[str, Any]:
        """创建IP账号"""
        ts = now_iso()
        account_data = {
            "character_name": character_name,
            "platform": platform,
            "account_name": account_name,
            "account_url": account_url,
            "follower_count": follower_count,
            "total_views": total_views,
            "total_likes": total_likes,
            "bio": bio,
            "is_active": is_active,
            "created_at": ts,
            "updated_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_ip_account",
            "resource_type": "ip_account",
            "resource_id": f"ip_{character_name}_{platform}_{ts}",
            "details": json.dumps(account_data, ensure_ascii=False),
        })
        account_data["account_id"] = f"ip_{character_name}_{platform}_{ts}"
        return account_data

    def list_ip_accounts(self, conn, character_name: Optional[str] = None,
                         platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出IP账号"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_ip_account":
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

    def update_ip_account_metrics(self, conn, account_id: str,
                                  follower_count: Optional[int] = None,
                                  total_views: Optional[int] = None,
                                  total_likes: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """更新IP账号数据"""
        logs = crud.audit_log_list(conn)
        for log in logs:
            if (log.get("action") == "create_ip_account" and
                    log.get("resource_id") == account_id):
                try:
                    data = json.loads(log.get("details", "{}"))
                except json.JSONDecodeError:
                    continue
                if follower_count is not None:
                    data["follower_count"] = follower_count
                if total_views is not None:
                    data["total_views"] = total_views
                if total_likes is not None:
                    data["total_likes"] = total_likes
                data["updated_at"] = now_iso()
                crud.audit_log_update(conn, log["id"], {
                    "details": json.dumps(data, ensure_ascii=False),
                })
                return data
        return None


class ContentPublishingPlan:
    """内容发布计划

    管理IP人物的内容发布计划和进度。
    """

    def create_publishing_plan(self, conn, account_id: str,
                               content_title: str,
                               content_type: str,
                               scheduled_publish_time: str,
                               story_type: Optional[str] = None,
                               product_category: Optional[str] = None,
                               status: str = "pending") -> Dict[str, Any]:
        """创建内容发布计划"""
        ts = now_iso()
        plan_data = {
            "account_id": account_id,
            "content_title": content_title,
            "content_type": content_type,
            "scheduled_publish_time": scheduled_publish_time,
            "story_type": story_type,
            "product_category": product_category,
            "status": status,
            "actual_publish_time": None,
            "created_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_publishing_plan",
            "resource_type": "publishing_plan",
            "resource_id": f"plan_{account_id}_{ts}",
            "details": json.dumps(plan_data, ensure_ascii=False),
        })
        plan_data["plan_id"] = f"plan_{account_id}_{ts}"
        return plan_data

    def list_publishing_plans(self, conn, account_id: Optional[str] = None,
                              status: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出发布计划"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_publishing_plan":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if account_id and data.get("account_id") != account_id:
                continue
            if status and data.get("status") != status:
                continue
            results.append(data)
        return results


# ---------------------------------------------------------------------------
# 5. 商业化运营指标仪表板
# ---------------------------------------------------------------------------
class BusinessMetrics:
    """商业化运营指标仪表板

    计算获客成本、客单价、复购率、ROI等关键指标。
    """

    def calculate_cac(self, conn, total_acquisition_cost_cny: float,
                      new_customers: int) -> Optional[float]:
        """获客成本 CAC = 总获客成本 / 新客户数"""
        if new_customers <= 0:
            return None
        return round(total_acquisition_cost_cny / new_customers, 2)

    def calculate_aov(self, conn, total_revenue_cny: float,
                      total_orders: int) -> Optional[float]:
        """客单价 AOV = 总收入 / 总订单数"""
        if total_orders <= 0:
            return None
        return round(total_revenue_cny / total_orders, 2)

    def calculate_repeat_rate(self, conn, repeat_customers: int,
                              total_customers: int) -> Optional[float]:
        """复购率 = 复购客户数 / 总客户数"""
        if total_customers <= 0:
            return None
        return round(repeat_customers / total_customers * 100, 2)

    def calculate_roi(self, conn, total_revenue_cny: float,
                      total_cost_cny: float) -> Optional[float]:
        """投资回报率 ROI = (总收入 - 总成本) / 总成本"""
        if total_cost_cny <= 0:
            return None
        return round((total_revenue_cny - total_cost_cny) / total_cost_cny * 100, 2)

    def generate_business_dashboard(self, conn) -> Dict[str, Any]:
        """生成商业化运营指标仪表板"""
        # 从合同中获取已签约业务数据
        contracts = []
        logs = crud.audit_log_list(conn)
        for log in logs:
            if log.get("action") == "create_contract":
                try:
                    data = json.loads(log.get("details", "{}"))
                    contracts.append(data)
                except json.JSONDecodeError:
                    continue

        signed_contracts = [c for c in contracts if c.get("status") == "已签署"]
        total_contract_value = sum(c.get("contract_amount_cny", 0) for c in signed_contracts)
        total_orders = len(signed_contracts)

        # 从IP账号中获取粉丝数据
        ip_accounts = []
        for log in logs:
            if log.get("action") == "create_ip_account":
                try:
                    data = json.loads(log.get("details", "{}"))
                    ip_accounts.append(data)
                except json.JSONDecodeError:
                    continue

        total_followers = sum(a.get("follower_count", 0) for a in ip_accounts)
        total_ip_views = sum(a.get("total_views", 0) for a in ip_accounts)

        # 从样片中获取效果数据
        sample_ads = []
        for log in logs:
            if log.get("action") == "create_sample_ad":
                try:
                    data = json.loads(log.get("details", "{}"))
                    sample_ads.append(data)
                except json.JSONDecodeError:
                    continue

        total_sample_views = sum(s.get("views", 0) for s in sample_ads)
        total_sample_orders = sum(s.get("orders", 0) for s in sample_ads)

        # 计算关键指标
        cac = self.calculate_cac(conn, total_acquisition_cost_cny=0, new_customers=len(set(c.get("customer_id") for c in contracts)))
        aov = self.calculate_aov(conn, total_revenue_cny=total_contract_value, total_orders=total_orders)
        repeat_customers = len(set(c.get("customer_id") for c in signed_contracts if list(contracts).count(c) > 1))
        repeat_rate = self.calculate_repeat_rate(conn, repeat_customers=repeat_customers, total_customers=len(set(c.get("customer_id") for c in contracts)))
        roi = self.calculate_roi(conn, total_revenue_cny=total_contract_value, total_cost_cny=0)

        return {
            "generated_at": now_iso(),
            "customer_metrics": {
                "total_customers": len(set(c.get("customer_id") for c in contracts)),
                "signed_customers": len(set(c.get("customer_id") for c in signed_contracts)),
                "cac_cny": cac,
                "aov_cny": aov,
                "repeat_rate_percent": repeat_rate,
            },
            "revenue_metrics": {
                "total_contract_value_cny": round(total_contract_value, 2),
                "total_orders": total_orders,
                "roi_percent": roi,
            },
            "ip_metrics": {
                "total_ip_accounts": len(ip_accounts),
                "total_followers": total_followers,
                "total_ip_views": total_ip_views,
            },
            "content_metrics": {
                "total_sample_ads": len(sample_ads),
                "total_sample_views": total_sample_views,
                "total_sample_orders": total_sample_orders,
            },
        }


__all__ = [
    "CustomerProfile",
    "ContactRecord",
    "SalesOpportunity",
    "ServiceProduct",
    "ContractManagement",
    "SampleAd",
    "CharacterIPAccount",
    "ContentPublishingPlan",
    "BusinessMetrics",
    "now_iso",
]
