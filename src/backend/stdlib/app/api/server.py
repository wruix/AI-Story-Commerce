"""AI Story Commerce — HTTP API Server (stdlib http.server implementation)"""

import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from app.db.session import get_db, init_db
import app.crud.crud as crud

# Route patterns: (method, regex_pattern, handler_name)
ROUTES = [
    # Health
    ("GET", r"^/health$", "health"),
    # Projects
    ("GET", r"^/api/v1/projects$", "project_list"),
    ("POST", r"^/api/v1/projects$", "project_create"),
    ("GET", r"^/api/v1/projects/([^/]+)$", "project_get"),
    ("PUT", r"^/api/v1/projects/([^/]+)$", "project_update"),
    ("DELETE", r"^/api/v1/projects/([^/]+)$", "project_delete"),
    # Customers
    ("GET", r"^/api/v1/customers$", "customer_list"),
    ("POST", r"^/api/v1/customers$", "customer_create"),
    ("GET", r"^/api/v1/customers/([^/]+)$", "customer_get"),
    ("PUT", r"^/api/v1/customers/([^/]+)$", "customer_update"),
    ("DELETE", r"^/api/v1/customers/([^/]+)$", "customer_delete"),
    # Products
    ("GET", r"^/api/v1/products$", "product_list"),
    ("POST", r"^/api/v1/products$", "product_create"),
    ("GET", r"^/api/v1/products/([^/]+)$", "product_get"),
    ("PUT", r"^/api/v1/products/([^/]+)$", "product_update"),
    ("DELETE", r"^/api/v1/products/([^/]+)$", "product_delete"),
    # Characters
    ("GET", r"^/api/v1/characters$", "character_list"),
    ("POST", r"^/api/v1/characters$", "character_create"),
    ("GET", r"^/api/v1/characters/([^/]+)$", "character_get"),
    ("PUT", r"^/api/v1/characters/([^/]+)$", "character_update"),
    ("DELETE", r"^/api/v1/characters/([^/]+)$", "character_delete"),
    ("GET", r"^/api/v1/characters/core-ip$", "character_core_ip"),
    # Story Ideas
    ("GET", r"^/api/v1/story-ideas$", "story_idea_list"),
    ("POST", r"^/api/v1/story-ideas$", "story_idea_create"),
    ("GET", r"^/api/v1/story-ideas/([^/]+)$", "story_idea_get"),
    ("PUT", r"^/api/v1/story-ideas/([^/]+)$", "story_idea_update"),
    ("DELETE", r"^/api/v1/story-ideas/([^/]+)$", "story_idea_delete"),
    # Scripts
    ("GET", r"^/api/v1/scripts$", "script_list"),
    ("POST", r"^/api/v1/scripts$", "script_create"),
    ("GET", r"^/api/v1/scripts/([^/]+)$", "script_get"),
    ("PUT", r"^/api/v1/scripts/([^/]+)$", "script_update"),
    ("DELETE", r"^/api/v1/scripts/([^/]+)$", "script_delete"),
    ("GET", r"^/api/v1/scripts/([^/]+)/current$", "script_current"),
    # Storyboards
    ("GET", r"^/api/v1/storyboards$", "storyboard_list"),
    ("POST", r"^/api/v1/storyboards$", "storyboard_create"),
    ("GET", r"^/api/v1/storyboards/([^/]+)$", "storyboard_get"),
    ("PUT", r"^/api/v1/storyboards/([^/]+)$", "storyboard_update"),
    ("DELETE", r"^/api/v1/storyboards/([^/]+)$", "storyboard_delete"),
    # Production Tasks
    ("GET", r"^/api/v1/production-tasks$", "production_task_list"),
    ("POST", r"^/api/v1/production-tasks$", "production_task_create"),
    ("GET", r"^/api/v1/production-tasks/([^/]+)$", "production_task_get"),
    ("PUT", r"^/api/v1/production-tasks/([^/]+)$", "production_task_update"),
    ("DELETE", r"^/api/v1/production-tasks/([^/]+)$", "production_task_delete"),
    # Media Assets
    ("GET", r"^/api/v1/media-assets$", "media_asset_list"),
    ("POST", r"^/api/v1/media-assets$", "media_asset_create"),
    ("GET", r"^/api/v1/media-assets/([^/]+)$", "media_asset_get"),
    ("PUT", r"^/api/v1/media-assets/([^/]+)$", "media_asset_update"),
    ("DELETE", r"^/api/v1/media-assets/([^/]+)$", "media_asset_delete"),
    # Advertisements
    ("GET", r"^/api/v1/advertisements$", "advertisement_list"),
    ("POST", r"^/api/v1/advertisements$", "advertisement_create"),
    ("GET", r"^/api/v1/advertisements/([^/]+)$", "advertisement_get"),
    ("PUT", r"^/api/v1/advertisements/([^/]+)$", "advertisement_update"),
    ("DELETE", r"^/api/v1/advertisements/([^/]+)$", "advertisement_delete"),
    # Compliance Reviews
    ("GET", r"^/api/v1/compliance-reviews$", "compliance_review_list"),
    ("POST", r"^/api/v1/compliance-reviews$", "compliance_review_create"),
    ("GET", r"^/api/v1/compliance-reviews/([^/]+)$", "compliance_review_get"),
    ("PUT", r"^/api/v1/compliance-reviews/([^/]+)$", "compliance_review_update"),
    ("DELETE", r"^/api/v1/compliance-reviews/([^/]+)$", "compliance_review_delete"),
    # Publishing Records
    ("GET", r"^/api/v1/publishing-records$", "publishing_record_list"),
    ("POST", r"^/api/v1/publishing-records$", "publishing_record_create"),
    ("GET", r"^/api/v1/publishing-records/([^/]+)$", "publishing_record_get"),
    ("PUT", r"^/api/v1/publishing-records/([^/]+)$", "publishing_record_update"),
    ("DELETE", r"^/api/v1/publishing-records/([^/]+)$", "publishing_record_delete"),
    # Performance Metrics
    ("GET", r"^/api/v1/performance-metrics$", "performance_metric_list"),
    ("POST", r"^/api/v1/performance-metrics$", "performance_metric_create"),
    ("GET", r"^/api/v1/performance-metrics/([^/]+)$", "performance_metric_get"),
    ("PUT", r"^/api/v1/performance-metrics/([^/]+)$", "performance_metric_update"),
    ("DELETE", r"^/api/v1/performance-metrics/([^/]+)$", "performance_metric_delete"),
    # Prompt Templates
    ("GET", r"^/api/v1/prompt-templates$", "prompt_template_list"),
    ("POST", r"^/api/v1/prompt-templates$", "prompt_template_create"),
    ("GET", r"^/api/v1/prompt-templates/([^/]+)$", "prompt_template_get"),
    ("PUT", r"^/api/v1/prompt-templates/([^/]+)$", "prompt_template_update"),
    ("DELETE", r"^/api/v1/prompt-templates/([^/]+)$", "prompt_template_delete"),
    # Audit Logs
    ("GET", r"^/api/v1/audit-logs$", "audit_log_list"),
    ("POST", r"^/api/v1/audit-logs$", "audit_log_create"),
    ("GET", r"^/api/v1/audit-logs/([^/]+)$", "audit_log_get"),
]


def _extract_id(path, pattern):
    m = re.match(pattern, path)
    return m.group(1) if m else None


class APIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for AI Story Commerce API."""

    def log_message(self, format, *args):
        # Suppress default logging for cleaner output
        pass

    def _send_json(self, status_code, data):
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8")) if raw else None

    def _get_query_params(self):
        parsed = urlparse(self.path)
        return parse_qs(parsed.query)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = self._get_query_params()

        for method, pattern, handler in ROUTES:
            if method != "GET":
                continue
            m = re.match(pattern, path)
            if not m:
                continue

            with get_db() as conn:
                if handler == "health":
                    self._send_json(200, {"status": "healthy", "service": "AI Story Commerce", "version": "0.1.0"})
                elif handler == "project_list":
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.project_list(conn, skip=skip, limit=limit))
                elif handler == "project_get":
                    pid = _extract_id(path, pattern)
                    obj = crud.project_get(conn, pid)
                    if not obj:
                        self._send_json(404, {"detail": "Project not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "customer_list":
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.customer_list(conn, skip=skip, limit=limit))
                elif handler == "customer_get":
                    cid = _extract_id(path, pattern)
                    obj = crud.customer_get(conn, cid)
                    if not obj:
                        self._send_json(404, {"detail": "Customer not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "product_list":
                    project_id = params.get("project_id", [None])[0]
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.product_list(conn, project_id=project_id, skip=skip, limit=limit))
                elif handler == "product_get":
                    pid = _extract_id(path, pattern)
                    obj = crud.product_get(conn, pid)
                    if not obj:
                        self._send_json(404, {"detail": "Product not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "character_list":
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.character_list(conn, skip=skip, limit=limit))
                elif handler == "character_get":
                    cid = _extract_id(path, pattern)
                    obj = crud.character_get(conn, cid)
                    if not obj:
                        self._send_json(404, {"detail": "Character not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "character_core_ip":
                    obj = crud.character_get_core_ip(conn)
                    self._send_json(200, obj if obj else {})
                elif handler == "story_idea_list":
                    product_id = params.get("product_id", [None])[0]
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.story_idea_list(conn, product_id=product_id, skip=skip, limit=limit))
                elif handler == "story_idea_get":
                    sid = _extract_id(path, pattern)
                    obj = crud.story_idea_get(conn, sid)
                    if not obj:
                        self._send_json(404, {"detail": "Story idea not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "script_list":
                    story_idea_id = params.get("story_idea_id", [None])[0]
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.script_list(conn, story_idea_id=story_idea_id, skip=skip, limit=limit))
                elif handler == "script_get":
                    sid = _extract_id(path, pattern)
                    obj = crud.script_get(conn, sid)
                    if not obj:
                        self._send_json(404, {"detail": "Script not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "script_current":
                    sid = _extract_id(path, pattern)
                    obj = crud.script_get_current(conn, sid)
                    if not obj:
                        self._send_json(404, {"detail": "Current script not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "storyboard_list":
                    script_id = params.get("script_id", [None])[0]
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.storyboard_list(conn, script_id=script_id, skip=skip, limit=limit))
                elif handler == "storyboard_get":
                    sid = _extract_id(path, pattern)
                    obj = crud.storyboard_get(conn, sid)
                    if not obj:
                        self._send_json(404, {"detail": "Storyboard not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "production_task_list":
                    storyboard_id = params.get("storyboard_id", [None])[0]
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.production_task_list(conn, storyboard_id=storyboard_id, skip=skip, limit=limit))
                elif handler == "production_task_get":
                    tid = _extract_id(path, pattern)
                    obj = crud.production_task_get(conn, tid)
                    if not obj:
                        self._send_json(404, {"detail": "Production task not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "media_asset_list":
                    storyboard_id = params.get("storyboard_id", [None])[0]
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.media_asset_list(conn, storyboard_id=storyboard_id, skip=skip, limit=limit))
                elif handler == "media_asset_get":
                    mid = _extract_id(path, pattern)
                    obj = crud.media_asset_get(conn, mid)
                    if not obj:
                        self._send_json(404, {"detail": "Media asset not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "advertisement_list":
                    project_id = params.get("project_id", [None])[0]
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.advertisement_list(conn, project_id=project_id, skip=skip, limit=limit))
                elif handler == "advertisement_get":
                    aid = _extract_id(path, pattern)
                    obj = crud.advertisement_get(conn, aid)
                    if not obj:
                        self._send_json(404, {"detail": "Advertisement not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "compliance_review_list":
                    advertisement_id = params.get("advertisement_id", [None])[0]
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.compliance_review_list(conn, advertisement_id=advertisement_id, skip=skip, limit=limit))
                elif handler == "compliance_review_get":
                    rid = _extract_id(path, pattern)
                    obj = crud.compliance_review_get(conn, rid)
                    if not obj:
                        self._send_json(404, {"detail": "Compliance review not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "publishing_record_list":
                    advertisement_id = params.get("advertisement_id", [None])[0]
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.publishing_record_list(conn, advertisement_id=advertisement_id, skip=skip, limit=limit))
                elif handler == "publishing_record_get":
                    rid = _extract_id(path, pattern)
                    obj = crud.publishing_record_get(conn, rid)
                    if not obj:
                        self._send_json(404, {"detail": "Publishing record not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "performance_metric_list":
                    publishing_record_id = params.get("publishing_record_id", [None])[0]
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.performance_metric_list(conn, publishing_record_id=publishing_record_id, skip=skip, limit=limit))
                elif handler == "performance_metric_get":
                    mid = _extract_id(path, pattern)
                    obj = crud.performance_metric_get(conn, mid)
                    if not obj:
                        self._send_json(404, {"detail": "Performance metric not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "prompt_template_list":
                    agent_type = params.get("agent_type", [None])[0]
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.prompt_template_list(conn, agent_type=agent_type, skip=skip, limit=limit))
                elif handler == "prompt_template_get":
                    tid = _extract_id(path, pattern)
                    obj = crud.prompt_template_get(conn, tid)
                    if not obj:
                        self._send_json(404, {"detail": "Prompt template not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "audit_log_list":
                    skip = int(params.get("skip", ["0"])[0])
                    limit = int(params.get("limit", ["100"])[0])
                    self._send_json(200, crud.audit_log_list(conn, skip=skip, limit=limit))
                elif handler == "audit_log_get":
                    lid = _extract_id(path, pattern)
                    obj = crud.audit_log_get(conn, lid)
                    if not obj:
                        self._send_json(404, {"detail": "Audit log not found"})
                    else:
                        self._send_json(200, obj)
            return

        self._send_json(404, {"detail": "Not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_body()

        for method, pattern, handler in ROUTES:
            if method != "POST":
                continue
            m = re.match(pattern, path)
            if not m:
                continue

            with get_db() as conn:
                if handler == "project_create":
                    obj = crud.project_create(conn, body)
                    self._send_json(201, obj)
                elif handler == "customer_create":
                    obj = crud.customer_create(conn, body)
                    self._send_json(201, obj)
                elif handler == "product_create":
                    obj = crud.product_create(conn, body)
                    self._send_json(201, obj)
                elif handler == "character_create":
                    obj = crud.character_create(conn, body)
                    self._send_json(201, obj)
                elif handler == "story_idea_create":
                    obj = crud.story_idea_create(conn, body)
                    self._send_json(201, obj)
                elif handler == "script_create":
                    obj = crud.script_create(conn, body)
                    self._send_json(201, obj)
                elif handler == "storyboard_create":
                    obj = crud.storyboard_create(conn, body)
                    self._send_json(201, obj)
                elif handler == "production_task_create":
                    obj = crud.production_task_create(conn, body)
                    self._send_json(201, obj)
                elif handler == "media_asset_create":
                    obj = crud.media_asset_create(conn, body)
                    self._send_json(201, obj)
                elif handler == "advertisement_create":
                    obj = crud.advertisement_create(conn, body)
                    self._send_json(201, obj)
                elif handler == "compliance_review_create":
                    obj = crud.compliance_review_create(conn, body)
                    self._send_json(201, obj)
                elif handler == "publishing_record_create":
                    obj = crud.publishing_record_create(conn, body)
                    self._send_json(201, obj)
                elif handler == "performance_metric_create":
                    obj = crud.performance_metric_create(conn, body)
                    self._send_json(201, obj)
                elif handler == "prompt_template_create":
                    obj = crud.prompt_template_create(conn, body)
                    self._send_json(201, obj)
                elif handler == "audit_log_create":
                    obj = crud.audit_log_create(conn, body)
                    self._send_json(201, obj)
            return

        self._send_json(404, {"detail": "Not found"})

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_body()

        for method, pattern, handler in ROUTES:
            if method != "PUT":
                continue
            m = re.match(pattern, path)
            if not m:
                continue

            resource_id = m.group(1)
            with get_db() as conn:
                if handler == "project_update":
                    obj = crud.project_update(conn, resource_id, body)
                    if not obj:
                        self._send_json(404, {"detail": "Project not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "customer_update":
                    obj = crud.customer_update(conn, resource_id, body)
                    if not obj:
                        self._send_json(404, {"detail": "Customer not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "product_update":
                    obj = crud.product_update(conn, resource_id, body)
                    if not obj:
                        self._send_json(404, {"detail": "Product not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "character_update":
                    obj = crud.character_update(conn, resource_id, body)
                    if not obj:
                        self._send_json(404, {"detail": "Character not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "story_idea_update":
                    obj = crud.story_idea_update(conn, resource_id, body)
                    if not obj:
                        self._send_json(404, {"detail": "Story idea not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "script_update":
                    obj = crud.script_update(conn, resource_id, body)
                    if not obj:
                        self._send_json(404, {"detail": "Script not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "storyboard_update":
                    obj = crud.storyboard_update(conn, resource_id, body)
                    if not obj:
                        self._send_json(404, {"detail": "Storyboard not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "production_task_update":
                    obj = crud.production_task_update(conn, resource_id, body)
                    if not obj:
                        self._send_json(404, {"detail": "Production task not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "media_asset_update":
                    obj = crud.media_asset_update(conn, resource_id, body)
                    if not obj:
                        self._send_json(404, {"detail": "Media asset not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "advertisement_update":
                    obj = crud.advertisement_update(conn, resource_id, body)
                    if not obj:
                        self._send_json(404, {"detail": "Advertisement not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "compliance_review_update":
                    obj = crud.compliance_review_update(conn, resource_id, body)
                    if not obj:
                        self._send_json(404, {"detail": "Compliance review not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "publishing_record_update":
                    obj = crud.publishing_record_update(conn, resource_id, body)
                    if not obj:
                        self._send_json(404, {"detail": "Publishing record not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "performance_metric_update":
                    obj = crud.performance_metric_update(conn, resource_id, body)
                    if not obj:
                        self._send_json(404, {"detail": "Performance metric not found"})
                    else:
                        self._send_json(200, obj)
                elif handler == "prompt_template_update":
                    obj = crud.prompt_template_update(conn, resource_id, body)
                    if not obj:
                        self._send_json(404, {"detail": "Prompt template not found"})
                    else:
                        self._send_json(200, obj)
            return

        self._send_json(404, {"detail": "Not found"})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        for method, pattern, handler in ROUTES:
            if method != "DELETE":
                continue
            m = re.match(pattern, path)
            if not m:
                continue

            resource_id = m.group(1)
            with get_db() as conn:
                if handler == "project_delete":
                    obj = crud.project_delete(conn, resource_id)
                    if not obj:
                        self._send_json(404, {"detail": "Project not found"})
                    else:
                        self._send_json(200, {"message": "Project deleted"})
                elif handler == "customer_delete":
                    obj = crud.customer_delete(conn, resource_id)
                    if not obj:
                        self._send_json(404, {"detail": "Customer not found"})
                    else:
                        self._send_json(200, {"message": "Customer deleted"})
                elif handler == "product_delete":
                    obj = crud.product_delete(conn, resource_id)
                    if not obj:
                        self._send_json(404, {"detail": "Product not found"})
                    else:
                        self._send_json(200, {"message": "Product deleted"})
                elif handler == "character_delete":
                    obj = crud.character_delete(conn, resource_id)
                    if not obj:
                        self._send_json(404, {"detail": "Character not found"})
                    else:
                        self._send_json(200, {"message": "Character deleted"})
                elif handler == "story_idea_delete":
                    obj = crud.story_idea_delete(conn, resource_id)
                    if not obj:
                        self._send_json(404, {"detail": "Story idea not found"})
                    else:
                        self._send_json(200, {"message": "Story idea deleted"})
                elif handler == "script_delete":
                    obj = crud.script_delete(conn, resource_id)
                    if not obj:
                        self._send_json(404, {"detail": "Script not found"})
                    else:
                        self._send_json(200, {"message": "Script deleted"})
                elif handler == "storyboard_delete":
                    obj = crud.storyboard_delete(conn, resource_id)
                    if not obj:
                        self._send_json(404, {"detail": "Storyboard not found"})
                    else:
                        self._send_json(200, {"message": "Storyboard deleted"})
                elif handler == "production_task_delete":
                    obj = crud.production_task_delete(conn, resource_id)
                    if not obj:
                        self._send_json(404, {"detail": "Production task not found"})
                    else:
                        self._send_json(200, {"message": "Production task deleted"})
                elif handler == "media_asset_delete":
                    obj = crud.media_asset_delete(conn, resource_id)
                    if not obj:
                        self._send_json(404, {"detail": "Media asset not found"})
                    else:
                        self._send_json(200, {"message": "Media asset deleted"})
                elif handler == "advertisement_delete":
                    obj = crud.advertisement_delete(conn, resource_id)
                    if not obj:
                        self._send_json(404, {"detail": "Advertisement not found"})
                    else:
                        self._send_json(200, {"message": "Advertisement deleted"})
                elif handler == "compliance_review_delete":
                    obj = crud.compliance_review_delete(conn, resource_id)
                    if not obj:
                        self._send_json(404, {"detail": "Compliance review not found"})
                    else:
                        self._send_json(200, {"message": "Compliance review deleted"})
                elif handler == "publishing_record_delete":
                    obj = crud.publishing_record_delete(conn, resource_id)
                    if not obj:
                        self._send_json(404, {"detail": "Publishing record not found"})
                    else:
                        self._send_json(200, {"message": "Publishing record deleted"})
                elif handler == "performance_metric_delete":
                    obj = crud.performance_metric_delete(conn, resource_id)
                    if not obj:
                        self._send_json(404, {"detail": "Performance metric not found"})
                    else:
                        self._send_json(200, {"message": "Performance metric deleted"})
                elif handler == "prompt_template_delete":
                    obj = crud.prompt_template_delete(conn, resource_id)
                    if not obj:
                        self._send_json(404, {"detail": "Prompt template not found"})
                    else:
                        self._send_json(200, {"message": "Prompt template deleted"})
            return

        self._send_json(404, {"detail": "Not found"})


def run(host="127.0.0.1", port=8000):
    init_db()
    server = HTTPServer((host, port), APIHandler)
    print(f"AI Story Commerce API running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


if __name__ == "__main__":
    run()
