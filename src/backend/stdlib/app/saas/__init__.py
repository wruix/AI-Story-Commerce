"""AI Story Commerce — G11 SaaS 产品化模块

对应立项方案商业战略第三阶段：将内部生产能力产品化为SaaS

实现：
1. 多租户 SaaS 架构：租户管理、租户隔离、白标部署
2. 客户自助注册与订阅管理：套餐定价、订阅生命周期、续费
3. 支付与账单管理：支付方式、发票、账单明细、退款
4. API 访问与集成：API密钥、使用配额、速率限制、Webhook
5. 用量计量与计费：按使用量计费、余额预警、自动扣费
6. SaaS 管理员后台：租户概览、收入分析、系统监控、运维
"""

import json
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from app.db.session import get_db
import app.crud.crud as crud


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# 1. 多租户 SaaS 架构
# ---------------------------------------------------------------------------
class Tenant:
    """多租户管理

    实现多租户架构，每个租户拥有独立的数据空间、配置和品牌标识。
    支持白标部署。
    """

    TENANT_STATUSES = [
        "active", "suspended", "cancelled", "trial", "expired",
    ]

    TENANT_PLANS = [
        "starter", "professional", "enterprise",
    ]

    def create_tenant(self, conn, tenant_name: str,
                      subdomain: str,
                      plan: str = "starter",
                      status: str = "trial",
                      owner_email: Optional[str] = None,
                      company_name: Optional[str] = None,
                      custom_domain: Optional[str] = None,
                      logo_url: Optional[str] = None,
                      primary_color: Optional[str] = None,
                      trial_ends_at: Optional[str] = None) -> Dict[str, Any]:
        """创建租户"""
        if plan not in self.TENANT_PLANS:
            raise ValueError(f"无效的套餐计划：{plan}")
        if status not in self.TENANT_STATUSES:
            raise ValueError(f"无效的租户状态：{status}")

        ts = now_iso()
        tenant_data = {
            "tenant_name": tenant_name,
            "subdomain": subdomain,
            "plan": plan,
            "status": status,
            "owner_email": owner_email,
            "company_name": company_name,
            "custom_domain": custom_domain,
            "logo_url": logo_url,
            "primary_color": primary_color,
            "trial_ends_at": trial_ends_at,
            "created_at": ts,
            "updated_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_tenant",
            "resource_type": "tenant",
            "resource_id": f"tenant_{subdomain}_{ts}",
            "details": json.dumps(tenant_data, ensure_ascii=False),
        })
        tenant_data["tenant_id"] = f"tenant_{subdomain}_{ts}"
        return tenant_data

    def list_tenants(self, conn, status: Optional[str] = None,
                     plan: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出租户"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_tenant":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if status and data.get("status") != status:
                continue
            if plan and data.get("plan") != plan:
                continue
            results.append(data)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results

    def update_tenant(self, conn, tenant_id: str,
                      status: Optional[str] = None,
                      plan: Optional[str] = None,
                      primary_color: Optional[str] = None,
                      logo_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """更新租户信息"""
        if status and status not in self.TENANT_STATUSES:
            raise ValueError(f"无效的租户状态：{status}")
        if plan and plan not in self.TENANT_PLANS:
            raise ValueError(f"无效的套餐计划：{plan}")

        logs = crud.audit_log_list(conn)
        for log in logs:
            if (log.get("action") == "create_tenant" and
                    log.get("resource_id") == tenant_id):
                try:
                    data = json.loads(log.get("details", "{}"))
                except json.JSONDecodeError:
                    continue
                if status:
                    data["status"] = status
                if plan:
                    data["plan"] = plan
                if primary_color:
                    data["primary_color"] = primary_color
                if logo_url:
                    data["logo_url"] = logo_url
                data["updated_at"] = now_iso()
                crud.audit_log_update(conn, log["id"], {
                    "details": json.dumps(data, ensure_ascii=False),
                })
                return data
        return None


# ---------------------------------------------------------------------------
# 2. 客户自助注册与订阅管理
# ---------------------------------------------------------------------------
class SubscriptionPlan:
    """订阅套餐定义

    定义SaaS产品的不同套餐，包括功能限制、价格、计费方式。
    """

    def __init__(self):
        self.default_plans = [
            {
                "plan_name": "starter",
                "display_name": "启动版",
                "price_cny": 99.0,
                "billing_cycle": "month",
                "max_ads_per_month": 10,
                "max_characters": 1,
                "max_storage_gb": 5,
                "api_calls_per_month": 1000,
                "features": ["基础剧情广告", "单角色IP", "邮箱支持"],
            },
            {
                "plan_name": "professional",
                "display_name": "专业版",
                "price_cny": 299.0,
                "billing_cycle": "month",
                "max_ads_per_month": 50,
                "max_characters": 5,
                "max_storage_gb": 50,
                "api_calls_per_month": 10000,
                "features": ["高级剧情广告", "多角色IP", "优先支持", "API访问"],
            },
            {
                "plan_name": "enterprise",
                "display_name": "企业版",
                "price_cny": 999.0,
                "billing_cycle": "month",
                "max_ads_per_month": -1,  # unlimited
                "max_characters": -1,  # unlimited
                "max_storage_gb": -1,  # unlimited
                "api_calls_per_month": -1,  # unlimited
                "features": ["全功能", "无限角色IP", "专属客户经理", "API访问", "白标部署"],
            },
        ]

    def list_plans(self) -> List[Dict[str, Any]]:
        """列出所有订阅套餐"""
        return self.default_plans

    def get_plan(self, plan_name: str) -> Optional[Dict[str, Any]]:
        """获取指定套餐详情"""
        for plan in self.default_plans:
            if plan["plan_name"] == plan_name:
                return plan
        return None


class Subscription:
    """订阅管理

    管理客户的订阅生命周期：创建、激活、续费、取消、暂停。
    """

    SUBSCRIPTION_STATUSES = [
        "active", "past_due", "canceled", "unpaid", "trialing",
    ]

    def create_subscription(self, conn, tenant_id: str,
                            plan_name: str,
                            price_cny: float,
                            billing_cycle: str = "month",
                            starts_at: Optional[str] = None,
                            ends_at: Optional[str] = None,
                            trial_ends_at: Optional[str] = None,
                            status: str = "trialing") -> Dict[str, Any]:
        """创建订阅"""
        if status not in self.SUBSCRIPTION_STATUSES:
            raise ValueError(f"无效的订阅状态：{status}")

        ts = now_iso()
        sub_data = {
            "tenant_id": tenant_id,
            "plan_name": plan_name,
            "price_cny": price_cny,
            "billing_cycle": billing_cycle,
            "starts_at": starts_at or ts,
            "ends_at": ends_at,
            "trial_ends_at": trial_ends_at,
            "status": status,
            "created_at": ts,
            "updated_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_subscription",
            "resource_type": "subscription",
            "resource_id": f"sub_{tenant_id}_{ts}",
            "details": json.dumps(sub_data, ensure_ascii=False),
        })
        sub_data["subscription_id"] = f"sub_{tenant_id}_{ts}"
        return sub_data

    def list_subscriptions(self, conn, tenant_id: Optional[str] = None,
                           status: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出订阅"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_subscription":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if tenant_id and data.get("tenant_id") != tenant_id:
                continue
            if status and data.get("status") != status:
                continue
            results.append(data)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results

    def update_subscription_status(self, conn, subscription_id: str,
                                   status: str) -> Optional[Dict[str, Any]]:
        """更新订阅状态"""
        if status not in self.SUBSCRIPTION_STATUSES:
            raise ValueError(f"无效的订阅状态：{status}")

        logs = crud.audit_log_list(conn)
        for log in logs:
            if (log.get("action") == "create_subscription" and
                    log.get("resource_id") == subscription_id):
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
# 3. 支付与账单管理
# ---------------------------------------------------------------------------
class PaymentMethod:
    """支付方式管理

    管理客户的支付方式，包括支付宝、微信支付、银行卡、信用卡等。
    """

    PAYMENT_TYPES = [
        "alipay", "wechat_pay", "bank_card", "credit_card", "paypal",
    ]

    def add_payment_method(self, conn, tenant_id: str,
                           payment_type: str,
                           account_last4: Optional[str] = None,
                           is_default: bool = False) -> Dict[str, Any]:
        """添加支付方式"""
        if payment_type not in self.PAYMENT_TYPES:
            raise ValueError(f"无效的支付方式：{payment_type}")

        ts = now_iso()
        pm_data = {
            "tenant_id": tenant_id,
            "payment_type": payment_type,
            "account_last4": account_last4,
            "is_default": is_default,
            "created_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "add_payment_method",
            "resource_type": "payment_method",
            "resource_id": f"pm_{tenant_id}_{ts}",
            "details": json.dumps(pm_data, ensure_ascii=False),
        })
        pm_data["payment_method_id"] = f"pm_{tenant_id}_{ts}"
        return pm_data

    def list_payment_methods(self, conn, tenant_id: str) -> List[Dict[str, Any]]:
        """列出支付方式"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "add_payment_method":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if data.get("tenant_id") != tenant_id:
                continue
            results.append(data)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results


class Invoice:
    """发票管理

    管理客户的发票开具，包括发票类型、抬头、税率、状态。
    """

    INVOICE_STATUSES = [
        "draft", "issued", "paid", "voided",
    ]

    def create_invoice(self, conn, tenant_id: str,
                       amount_cny: float,
                       tax_amount_cny: float,
                       invoice_title: str,
                       tax_id: Optional[str] = None,
                       status: str = "draft") -> Dict[str, Any]:
        """创建发票"""
        if status not in self.INVOICE_STATUSES:
            raise ValueError(f"无效的发票状态：{status}")

        ts = now_iso()
        inv_data = {
            "tenant_id": tenant_id,
            "amount_cny": amount_cny,
            "tax_amount_cny": tax_amount_cny,
            "total_cny": round(amount_cny + tax_amount_cny, 2),
            "invoice_title": invoice_title,
            "tax_id": tax_id,
            "status": status,
            "created_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_invoice",
            "resource_type": "invoice",
            "resource_id": f"invoice_{tenant_id}_{ts}",
            "details": json.dumps(inv_data, ensure_ascii=False),
        })
        inv_data["invoice_id"] = f"invoice_{tenant_id}_{ts}"
        return inv_data

    def list_invoices(self, conn, tenant_id: Optional[str] = None,
                      status: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出发票"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_invoice":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if tenant_id and data.get("tenant_id") != tenant_id:
                continue
            if status and data.get("status") != status:
                continue
            results.append(data)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results


# ---------------------------------------------------------------------------
# 4. API 访问与集成
# ---------------------------------------------------------------------------
class ApiKey:
    """API 访问与集成管理

    管理客户的API密钥，包括密钥生成、使用配额、速率限制、Webhook。
    """

    def create_api_key(self, conn, tenant_id: str,
                       key_name: str,
                       rate_limit_per_minute: int = 60,
                       quota_per_month: Optional[int] = None,
                       scopes: Optional[List[str]] = None) -> Dict[str, Any]:
        """创建API密钥"""
        import uuid
        import hashlib

        ts = now_iso()
        raw_key = f"asc_{tenant_id}_{ts}_{uuid.uuid4().hex[:16]}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()[:32]

        key_data = {
            "tenant_id": tenant_id,
            "key_name": key_name,
            "key_prefix": "asc_",
            "key_hash": key_hash,
            "rate_limit_per_minute": rate_limit_per_minute,
            "quota_per_month": quota_per_month,
            "scopes": json.dumps(scopes or ["read", "write"], ensure_ascii=False),
            "is_active": True,
            "created_at": ts,
            "last_used_at": None,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_api_key",
            "resource_type": "api_key",
            "resource_id": f"apikey_{tenant_id}_{ts}",
            "details": json.dumps(key_data, ensure_ascii=False),
        })
        # Return raw key only once
        key_data["raw_key"] = raw_key
        key_data["api_key_id"] = f"apikey_{tenant_id}_{ts}"
        return key_data

    def list_api_keys(self, conn, tenant_id: str) -> List[Dict[str, Any]]:
        """列出API密钥（不返回原始密钥）"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_api_key":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if data.get("tenant_id") != tenant_id:
                continue
            # Remove raw_key from stored data
            data.pop("raw_key", None)
            results.append(data)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results


class Webhook:
    """Webhook 管理

    管理客户的Webhook端点，用于事件通知。
    """

    EVENT_TYPES = [
        "subscription.created", "subscription.updated", "subscription.canceled",
        "payment.succeeded", "payment.failed", "invoice.created", "invoice.paid",
        "ad.created", "ad.published", "quota.exceeded",
    ]

    def create_webhook(self, conn, tenant_id: str,
                       url: str,
                       event_types: Optional[List[str]] = None,
                       secret: Optional[str] = None,
                       is_active: bool = True) -> Dict[str, Any]:
        """创建Webhook端点"""
        import uuid

        ts = now_iso()
        wh_data = {
            "tenant_id": tenant_id,
            "url": url,
            "event_types": json.dumps(event_types or ["ad.published"], ensure_ascii=False),
            "secret": secret,
            "is_active": is_active,
            "created_at": ts,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "create_webhook",
            "resource_type": "webhook",
            "resource_id": f"webhook_{tenant_id}_{ts}",
            "details": json.dumps(wh_data, ensure_ascii=False),
        })
        wh_data["webhook_id"] = f"webhook_{tenant_id}_{ts}"
        return wh_data

    def list_webhooks(self, conn, tenant_id: str) -> List[Dict[str, Any]]:
        """列出Webhook端点"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "create_webhook":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if data.get("tenant_id") != tenant_id:
                continue
            # Remove secret
            data.pop("secret", None)
            results.append(data)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results


# ---------------------------------------------------------------------------
# 5. 用量计量与计费
# ---------------------------------------------------------------------------
class UsageMeter:
    """用量计量管理

    记录客户的API调用、广告生成、存储使用等计量数据。
    """

    METER_TYPES = [
        "api_call", "ad_generated", "storage_gb", "character_used",
    ]

    def record_usage(self, conn, tenant_id: str,
                     meter_type: str,
                     quantity: int,
                     recorded_at: Optional[str] = None,
                     metadata: Optional[str] = None) -> Dict[str, Any]:
        """记录用量"""
        if meter_type not in self.METER_TYPES:
            raise ValueError(f"无效的计量类型：{meter_type}")

        ts = recorded_at or now_iso()
        usage_data = {
            "tenant_id": tenant_id,
            "meter_type": meter_type,
            "quantity": quantity,
            "recorded_at": ts,
            "metadata": metadata,
        }
        crud.audit_log_create(conn, {
            "user_id": "system",
            "action": "record_usage",
            "resource_type": "usage_meter",
            "resource_id": f"usage_{tenant_id}_{meter_type}_{ts}",
            "details": json.dumps(usage_data, ensure_ascii=False),
        })
        usage_data["usage_id"] = f"usage_{tenant_id}_{meter_type}_{ts}"
        return usage_data

    def list_usage(self, conn, tenant_id: str,
                   meter_type: Optional[str] = None,
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出用量记录"""
        logs = crud.audit_log_list(conn)
        results = []
        for log in logs:
            if log.get("action") != "record_usage":
                continue
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if data.get("tenant_id") != tenant_id:
                continue
            if meter_type and data.get("meter_type") != meter_type:
                continue
            if start_date and data.get("recorded_at", "") < start_date:
                continue
            if end_date and data.get("recorded_at", "") > end_date:
                continue
            results.append(data)
        results.sort(key=lambda x: x.get("recorded_at", ""), reverse=True)
        return results

    def get_usage_summary(self, conn, tenant_id: str,
                          meter_type: str,
                          start_date: str,
                          end_date: str) -> Dict[str, Any]:
        """获取用量汇总"""
        usage_records = self.list_usage(conn, tenant_id, meter_type,
                                        start_date, end_date)
        total_quantity = sum(r.get("quantity", 0) for r in usage_records)
        return {
            "tenant_id": tenant_id,
            "meter_type": meter_type,
            "start_date": start_date,
            "end_date": end_date,
            "total_quantity": total_quantity,
            "record_count": len(usage_records),
        }


# ---------------------------------------------------------------------------
# 6. SaaS 管理员后台
# ---------------------------------------------------------------------------
class AdminDashboard:
    """SaaS 管理员后台

    提供租户概览、收入分析、系统监控、运维等管理功能。
    """

    def get_tenant_overview(self, conn) -> Dict[str, Any]:
        """获取租户概览"""
        tenants = []
        logs = crud.audit_log_list(conn)
        for log in logs:
            if log.get("action") == "create_tenant":
                try:
                    data = json.loads(log.get("details", "{}"))
                    tenants.append(data)
                except json.JSONDecodeError:
                    continue

        total_tenants = len(tenants)
        active_tenants = sum(1 for t in tenants if t.get("status") == "active")
        trial_tenants = sum(1 for t in tenants if t.get("status") == "trial")
        suspended_tenants = sum(1 for t in tenants if t.get("status") == "suspended")

        plan_distribution = {}
        for t in tenants:
            p = t.get("plan", "unknown")
            plan_distribution[p] = plan_distribution.get(p, 0) + 1

        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "trial_tenants": trial_tenants,
            "suspended_tenants": suspended_tenants,
            "plan_distribution": plan_distribution,
        }

    def get_revenue_analysis(self, conn) -> Dict[str, Any]:
        """获取收入分析"""
        invoices = []
        subscriptions = []
        logs = crud.audit_log_list(conn)
        for log in logs:
            try:
                data = json.loads(log.get("details", "{}"))
            except json.JSONDecodeError:
                continue
            if log.get("action") == "create_invoice":
                if data.get("status") == "paid":
                    invoices.append(data)
            elif log.get("action") == "create_subscription":
                subscriptions.append(data)

        total_invoiced = sum(i.get("total_cny", 0) for i in invoices)
        total_subscriptions = len(subscriptions)
        active_subscriptions = sum(1 for s in subscriptions
                                   if s.get("status") == "active")

        return {
            "total_invoiced_cny": round(total_invoiced, 2),
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "paid_invoice_count": len(invoices),
        }

    def get_system_metrics(self, conn) -> Dict[str, Any]:
        """获取系统监控指标"""
        # Count various resource types
        metrics = {}
        logs = crud.audit_log_list(conn)
        for log in logs:
            action = log.get("action", "")
            if action.startswith("create_"):
                resource_type = action.replace("create_", "")
                metrics[resource_type] = metrics.get(resource_type, 0) + 1

        return {
            "resource_counts": metrics,
            "total_events": len(logs),
        }

    def get_admin_dashboard(self, conn) -> Dict[str, Any]:
        """获取完整的管理员仪表板"""
        return {
            "generated_at": now_iso(),
            "tenant_overview": self.get_tenant_overview(conn),
            "revenue_analysis": self.get_revenue_analysis(conn),
            "system_metrics": self.get_system_metrics(conn),
        }


__all__ = [
    "Tenant",
    "SubscriptionPlan",
    "Subscription",
    "PaymentMethod",
    "Invoice",
    "ApiKey",
    "Webhook",
    "UsageMeter",
    "AdminDashboard",
    "now_iso",
]
