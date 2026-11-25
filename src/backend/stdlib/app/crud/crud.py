"""AI Story Commerce — CRUD operations (stdlib sqlite3 implementation)"""

import uuid
from datetime import datetime, timezone
from app.db.session import get_db, generate_id, now_iso


def _row_to_dict(row):
    """Convert sqlite3.Row to dict."""
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


def _rows_to_dicts(rows):
    """Convert list of sqlite3.Row to list of dicts."""
    return [_row_to_dict(r) for r in rows]


# ===========================================================================
# Projects
# ===========================================================================
def project_create(conn, data):
    pid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO projects (id, name, description, status, customer_id, budget_cny, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (pid, data["name"], data.get("description"), data.get("status", "draft"),
         data.get("customer_id"), data.get("budget_cny"), now, now),
    )
    return project_get(conn, pid)


def project_get(conn, pid):
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (pid,)).fetchone()
    return _row_to_dict(row)


def project_list(conn, skip=0, limit=100):
    rows = conn.execute("SELECT * FROM projects ORDER BY created_at DESC LIMIT ? OFFSET ?",
                        (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def project_update(conn, pid, data):
    fields = []
    params = []
    for k, v in data.items():
        fields.append(f"{k} = ?")
        params.append(v)
    if not fields:
        return project_get(conn, pid)
    fields.append("updated_at = ?")
    params.append(now_iso())
    params.append(pid)
    conn.execute(f"UPDATE projects SET {', '.join(fields)} WHERE id = ?", params)
    return project_get(conn, pid)


def project_delete(conn, pid):
    row = project_get(conn, pid)
    if row:
        conn.execute("DELETE FROM projects WHERE id = ?", (pid,))
    return row


# ===========================================================================
# Customers
# ===========================================================================
def customer_create(conn, data):
    cid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO customers (id, name, contact_person, phone, email, company, address, notes, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (cid, data["name"], data.get("contact_person"), data.get("phone"), data.get("email"),
         data.get("company"), data.get("address"), data.get("notes"), now, now),
    )
    return customer_get(conn, cid)


def customer_get(conn, cid):
    row = conn.execute("SELECT * FROM customers WHERE id = ?", (cid,)).fetchone()
    return _row_to_dict(row)


def customer_list(conn, skip=0, limit=100):
    rows = conn.execute("SELECT * FROM customers ORDER BY created_at DESC LIMIT ? OFFSET ?",
                        (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def customer_update(conn, cid, data):
    fields = []
    params = []
    for k, v in data.items():
        fields.append(f"{k} = ?")
        params.append(v)
    if not fields:
        return customer_get(conn, cid)
    fields.append("updated_at = ?")
    params.append(now_iso())
    params.append(cid)
    conn.execute(f"UPDATE customers SET {', '.join(fields)} WHERE id = ?", params)
    return customer_get(conn, cid)


def customer_delete(conn, cid):
    row = customer_get(conn, cid)
    if row:
        conn.execute("DELETE FROM customers WHERE id = ?", (cid,))
    return row


# ===========================================================================
# Products
# ===========================================================================
def product_create(conn, data):
    pid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO products (id, project_id, name, category, price_cny, specifications, selling_points,
           target_audience, usage_scenarios, proof_materials, image_url, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (pid, data["project_id"], data["name"], data.get("category", "other"),
         data.get("price_cny"), data.get("specifications"), data.get("selling_points"),
         data.get("target_audience"), data.get("usage_scenarios"), data.get("proof_materials"),
         data.get("image_url"), now, now),
    )
    return product_get(conn, pid)


def product_get(conn, pid):
    row = conn.execute("SELECT * FROM products WHERE id = ?", (pid,)).fetchone()
    return _row_to_dict(row)


def product_list(conn, project_id=None, skip=0, limit=100):
    if project_id:
        rows = conn.execute(
            "SELECT * FROM products WHERE project_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (project_id, limit, skip),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM products ORDER BY created_at DESC LIMIT ? OFFSET ?",
                            (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def product_update(conn, pid, data):
    fields = []
    params = []
    for k, v in data.items():
        fields.append(f"{k} = ?")
        params.append(v)
    if not fields:
        return product_get(conn, pid)
    fields.append("updated_at = ?")
    params.append(now_iso())
    params.append(pid)
    conn.execute(f"UPDATE products SET {', '.join(fields)} WHERE id = ?", params)
    return product_get(conn, pid)


def product_delete(conn, pid):
    row = product_get(conn, pid)
    if row:
        conn.execute("DELETE FROM products WHERE id = ?", (pid,))
    return row


# ===========================================================================
# Characters
# ===========================================================================
def character_create(conn, data):
    cid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO characters (id, name, gender, age_range, background, personality, catchphrases,
           worldview, commercial_boundary, reference_image_url, voice_reference_url, is_core_ip,
           created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (cid, data["name"], data["gender"], data.get("age_range"), data.get("background"),
         data.get("personality"), data.get("catchphrases"), data.get("worldview"),
         data.get("commercial_boundary"), data.get("reference_image_url"), data.get("voice_reference_url"),
         1 if data.get("is_core_ip") else 0, now, now),
    )
    return character_get(conn, cid)


def character_get(conn, cid):
    row = conn.execute("SELECT * FROM characters WHERE id = ?", (cid,)).fetchone()
    return _row_to_dict(row)


def character_list(conn, skip=0, limit=100):
    rows = conn.execute("SELECT * FROM characters ORDER BY created_at DESC LIMIT ? OFFSET ?",
                        (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def character_get_core_ip(conn):
    row = conn.execute("SELECT * FROM characters WHERE is_core_ip = 1 LIMIT 1").fetchone()
    return _row_to_dict(row)


def character_update(conn, cid, data):
    fields = []
    params = []
    for k, v in data.items():
        if k == "is_core_ip":
            fields.append("is_core_ip = ?")
            params.append(1 if v else 0)
        else:
            fields.append(f"{k} = ?")
            params.append(v)
    if not fields:
        return character_get(conn, cid)
    fields.append("updated_at = ?")
    params.append(now_iso())
    params.append(cid)
    conn.execute(f"UPDATE characters SET {', '.join(fields)} WHERE id = ?", params)
    return character_get(conn, cid)


def character_delete(conn, cid):
    row = character_get(conn, cid)
    if row:
        conn.execute("DELETE FROM characters WHERE id = ?", (cid,))
    return row


# ===========================================================================
# Character Assets
# ===========================================================================
def character_asset_create(conn, data):
    aid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO character_assets (id, character_id, asset_type, file_path, sha256,
           description, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (aid, data["character_id"], data["asset_type"], data["file_path"],
         data.get("sha256"), data.get("description"), now),
    )
    return character_asset_get(conn, aid)


def character_asset_get(conn, aid):
    row = conn.execute("SELECT * FROM character_assets WHERE id = ?", (aid,)).fetchone()
    return _row_to_dict(row)


def character_asset_list(conn, character_id=None, skip=0, limit=100):
    if character_id:
        rows = conn.execute(
            "SELECT * FROM character_assets WHERE character_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (character_id, limit, skip),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM character_assets ORDER BY created_at DESC LIMIT ? OFFSET ?",
                            (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def character_asset_update(conn, aid, data):
    fields = []
    params = []
    for k, v in data.items():
        fields.append(f"{k} = ?")
        params.append(v)
    if not fields:
        return character_asset_get(conn, aid)
    params.append(aid)
    conn.execute(f"UPDATE character_assets SET {', '.join(fields)} WHERE id = ?", params)
    return character_asset_get(conn, aid)


def character_asset_delete(conn, aid):
    row = character_asset_get(conn, aid)
    if row:
        conn.execute("DELETE FROM character_assets WHERE id = ?", (aid,))
    return row


# ===========================================================================
# Story Ideas
# ===========================================================================
def story_idea_create(conn, data):
    sid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO story_ideas (id, product_id, title, description, story_type, hook, conflict, twist,
           product_integration, score, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (sid, data["product_id"], data["title"], data.get("description"), data.get("story_type"),
         data.get("hook"), data.get("conflict"), data.get("twist"), data.get("product_integration"),
         data.get("score"), data.get("status", "generated"), now),
    )
    return story_idea_get(conn, sid)


def story_idea_get(conn, sid):
    row = conn.execute("SELECT * FROM story_ideas WHERE id = ?", (sid,)).fetchone()
    return _row_to_dict(row)


def story_idea_list(conn, product_id=None, skip=0, limit=100):
    if product_id:
        rows = conn.execute(
            "SELECT * FROM story_ideas WHERE product_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (product_id, limit, skip),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM story_ideas ORDER BY created_at DESC LIMIT ? OFFSET ?",
                            (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def story_idea_update(conn, sid, data):
    fields = []
    params = []
    for k, v in data.items():
        fields.append(f"{k} = ?")
        params.append(v)
    if not fields:
        return story_idea_get(conn, sid)
    params.append(sid)
    conn.execute(f"UPDATE story_ideas SET {', '.join(fields)} WHERE id = ?", params)
    return story_idea_get(conn, sid)


def story_idea_delete(conn, sid):
    row = story_idea_get(conn, sid)
    if row:
        conn.execute("DELETE FROM story_ideas WHERE id = ?", (sid,))
    return row


# ===========================================================================
# Scripts
# ===========================================================================
def script_create(conn, data):
    sid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO scripts (id, story_idea_id, version, title, content, raw_ai_input, raw_ai_output,
           status, is_current, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (sid, data["story_idea_id"], data.get("version", 1), data["title"], data["content"],
         data.get("raw_ai_input"), data.get("raw_ai_output"), data.get("status", "draft"),
         1 if data.get("is_current") else 0, now),
    )
    return script_get(conn, sid)


def script_get(conn, sid):
    row = conn.execute("SELECT * FROM scripts WHERE id = ?", (sid,)).fetchone()
    return _row_to_dict(row)


def script_list(conn, story_idea_id=None, skip=0, limit=100):
    if story_idea_id:
        rows = conn.execute(
            "SELECT * FROM scripts WHERE story_idea_id = ? ORDER BY version DESC LIMIT ? OFFSET ?",
            (story_idea_id, limit, skip),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM scripts ORDER BY created_at DESC LIMIT ? OFFSET ?",
                            (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def script_get_current(conn, story_idea_id):
    row = conn.execute(
        "SELECT * FROM scripts WHERE story_idea_id = ? AND is_current = 1", (story_idea_id,)
    ).fetchone()
    return _row_to_dict(row)


def script_update(conn, sid, data):
    fields = []
    params = []
    for k, v in data.items():
        if k == "is_current":
            fields.append("is_current = ?")
            params.append(1 if v else 0)
        else:
            fields.append(f"{k} = ?")
            params.append(v)
    if not fields:
        return script_get(conn, sid)
    params.append(sid)
    conn.execute(f"UPDATE scripts SET {', '.join(fields)} WHERE id = ?", params)
    return script_get(conn, sid)


def script_delete(conn, sid):
    row = script_get(conn, sid)
    if row:
        conn.execute("DELETE FROM scripts WHERE id = ?", (sid,))
    return row


# ===========================================================================
# Storyboards
# ===========================================================================
def storyboard_create(conn, data):
    sid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO storyboards (id, script_id, shot_number, description, image_prompt, dialogue,
           sound_effect, duration_seconds, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (sid, data["script_id"], data["shot_number"], data.get("description"), data.get("image_prompt"),
         data.get("dialogue"), data.get("sound_effect"), data.get("duration_seconds"), now),
    )
    return storyboard_get(conn, sid)


def storyboard_get(conn, sid):
    row = conn.execute("SELECT * FROM storyboards WHERE id = ?", (sid,)).fetchone()
    return _row_to_dict(row)


def storyboard_list(conn, script_id=None, skip=0, limit=100):
    if script_id:
        rows = conn.execute(
            "SELECT * FROM storyboards WHERE script_id = ? ORDER BY shot_number LIMIT ? OFFSET ?",
            (script_id, limit, skip),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM storyboards ORDER BY created_at DESC LIMIT ? OFFSET ?",
                            (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def storyboard_update(conn, sid, data):
    fields = []
    params = []
    for k, v in data.items():
        fields.append(f"{k} = ?")
        params.append(v)
    if not fields:
        return storyboard_get(conn, sid)
    params.append(sid)
    conn.execute(f"UPDATE storyboards SET {', '.join(fields)} WHERE id = ?", params)
    return storyboard_get(conn, sid)


def storyboard_delete(conn, sid):
    row = storyboard_get(conn, sid)
    if row:
        conn.execute("DELETE FROM storyboards WHERE id = ?", (sid,))
    return row


# ===========================================================================
# Production Tasks
# ===========================================================================
def production_task_create(conn, data):
    tid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO production_tasks (id, storyboard_id, task_type, status, input_data, output_data,
           error_message, started_at, completed_at, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (tid, data.get("storyboard_id"), data["task_type"], data.get("status", "pending"),
         data.get("input_data"), data.get("output_data"), data.get("error_message"),
         data.get("started_at"), data.get("completed_at"), now),
    )
    return production_task_get(conn, tid)


def production_task_get(conn, tid):
    row = conn.execute("SELECT * FROM production_tasks WHERE id = ?", (tid,)).fetchone()
    return _row_to_dict(row)


def production_task_list(conn, storyboard_id=None, skip=0, limit=100):
    if storyboard_id:
        rows = conn.execute(
            "SELECT * FROM production_tasks WHERE storyboard_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (storyboard_id, limit, skip),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM production_tasks ORDER BY created_at DESC LIMIT ? OFFSET ?",
                            (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def production_task_update(conn, tid, data):
    fields = []
    params = []
    for k, v in data.items():
        fields.append(f"{k} = ?")
        params.append(v)
    if not fields:
        return production_task_get(conn, tid)
    params.append(tid)
    conn.execute(f"UPDATE production_tasks SET {', '.join(fields)} WHERE id = ?", params)
    return production_task_get(conn, tid)


def production_task_delete(conn, tid):
    row = production_task_get(conn, tid)
    if row:
        conn.execute("DELETE FROM production_tasks WHERE id = ?", (tid,))
    return row


# ===========================================================================
# Media Assets
# ===========================================================================
def media_asset_create(conn, data):
    mid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO media_assets (id, storyboard_id, production_task_id, media_type, file_path, sha256,
           file_size_bytes, duration_seconds, width, height, ai_generated, ai_disclosure, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (mid, data.get("storyboard_id"), data.get("production_task_id"), data["media_type"],
         data["file_path"], data.get("sha256"), data.get("file_size_bytes"), data.get("duration_seconds"),
         data.get("width"), data.get("height"),
         1 if data.get("ai_generated") else 0, 1 if data.get("ai_disclosure") else 0, now),
    )
    return media_asset_get(conn, mid)


def media_asset_get(conn, mid):
    row = conn.execute("SELECT * FROM media_assets WHERE id = ?", (mid,)).fetchone()
    return _row_to_dict(row)


def media_asset_list(conn, storyboard_id=None, skip=0, limit=100):
    if storyboard_id:
        rows = conn.execute(
            "SELECT * FROM media_assets WHERE storyboard_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (storyboard_id, limit, skip),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM media_assets ORDER BY created_at DESC LIMIT ? OFFSET ?",
                            (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def media_asset_update(conn, mid, data):
    fields = []
    params = []
    for k, v in data.items():
        if k in ("ai_generated", "ai_disclosure"):
            fields.append(f"{k} = ?")
            params.append(1 if v else 0)
        else:
            fields.append(f"{k} = ?")
            params.append(v)
    if not fields:
        return media_asset_get(conn, mid)
    params.append(mid)
    conn.execute(f"UPDATE media_assets SET {', '.join(fields)} WHERE id = ?", params)
    return media_asset_get(conn, mid)


def media_asset_delete(conn, mid):
    row = media_asset_get(conn, mid)
    if row:
        conn.execute("DELETE FROM media_assets WHERE id = ?", (mid,))
    return row


# ===========================================================================
# Advertisements
# ===========================================================================
def advertisement_create(conn, data):
    aid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO advertisements (id, project_id, script_id, version, title, file_path, sha256,
           duration_seconds, status, is_current, ai_disclosure, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (aid, data["project_id"], data.get("script_id"), data.get("version", 1), data["title"],
         data.get("file_path"), data.get("sha256"), data.get("duration_seconds"),
         data.get("status", "draft"), 1 if data.get("is_current") else 0,
         1 if data.get("ai_disclosure") else 0, now),
    )
    return advertisement_get(conn, aid)


def advertisement_get(conn, aid):
    row = conn.execute("SELECT * FROM advertisements WHERE id = ?", (aid,)).fetchone()
    return _row_to_dict(row)


def advertisement_list(conn, project_id=None, skip=0, limit=100):
    if project_id:
        rows = conn.execute(
            "SELECT * FROM advertisements WHERE project_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (project_id, limit, skip),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM advertisements ORDER BY created_at DESC LIMIT ? OFFSET ?",
                            (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def advertisement_update(conn, aid, data):
    fields = []
    params = []
    for k, v in data.items():
        if k in ("is_current", "ai_disclosure"):
            fields.append(f"{k} = ?")
            params.append(1 if v else 0)
        else:
            fields.append(f"{k} = ?")
            params.append(v)
    if not fields:
        return advertisement_get(conn, aid)
    params.append(aid)
    conn.execute(f"UPDATE advertisements SET {', '.join(fields)} WHERE id = ?", params)
    return advertisement_get(conn, aid)


def advertisement_delete(conn, aid):
    row = advertisement_get(conn, aid)
    if row:
        conn.execute("DELETE FROM advertisements WHERE id = ?", (aid,))
    return row


# ===========================================================================
# Compliance Reviews
# ===========================================================================
def compliance_review_create(conn, data):
    rid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO compliance_reviews (id, advertisement_id, reviewer_type, ai_disclosure_required,
           ai_disclosure_confirmed, product_authenticity, fictional_experience_check, portrait_authorization,
           voice_clone_authorization, music_license, trademark_check, ad_content_compliance, status, remarks,
           reviewed_at, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (rid, data["advertisement_id"], data["reviewer_type"],
         1 if data.get("ai_disclosure_required", True) else 0,
         1 if data.get("ai_disclosure_confirmed") else 0,
         data.get("product_authenticity"), data.get("fictional_experience_check"),
         data.get("portrait_authorization"), data.get("voice_clone_authorization"),
         data.get("music_license"), data.get("trademark_check"), data.get("ad_content_compliance"),
         data.get("status", "pending"), data.get("remarks"), data.get("reviewed_at"), now),
    )
    return compliance_review_get(conn, rid)


def compliance_review_get(conn, rid):
    row = conn.execute("SELECT * FROM compliance_reviews WHERE id = ?", (rid,)).fetchone()
    return _row_to_dict(row)


def compliance_review_list(conn, advertisement_id=None, skip=0, limit=100):
    if advertisement_id:
        rows = conn.execute(
            "SELECT * FROM compliance_reviews WHERE advertisement_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (advertisement_id, limit, skip),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM compliance_reviews ORDER BY created_at DESC LIMIT ? OFFSET ?",
                            (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def compliance_review_update(conn, rid, data):
    fields = []
    params = []
    for k, v in data.items():
        if k in ("ai_disclosure_required", "ai_disclosure_confirmed"):
            fields.append(f"{k} = ?")
            params.append(1 if v else 0)
        elif k in ("product_authenticity", "fictional_experience_check", "portrait_authorization",
                   "voice_clone_authorization", "music_license", "trademark_check", "ad_content_compliance"):
            fields.append(f"{k} = ?")
            params.append(1 if v else 0)
        else:
            fields.append(f"{k} = ?")
            params.append(v)
    if not fields:
        return compliance_review_get(conn, rid)
    params.append(rid)
    conn.execute(f"UPDATE compliance_reviews SET {', '.join(fields)} WHERE id = ?", params)
    return compliance_review_get(conn, rid)


def compliance_review_delete(conn, rid):
    row = compliance_review_get(conn, rid)
    if row:
        conn.execute("DELETE FROM compliance_reviews WHERE id = ?", (rid,))
    return row


# ===========================================================================
# Publishing Records
# ===========================================================================
def publishing_record_create(conn, data):
    rid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO publishing_records (id, advertisement_id, platform, account_name, publish_url,
           publish_time, ai_disclosure_posted, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (rid, data["advertisement_id"], data.get("platform", "douyin"), data.get("account_name"),
         data.get("publish_url"), data.get("publish_time"),
         1 if data.get("ai_disclosure_posted") else 0, now),
    )
    return publishing_record_get(conn, rid)


def publishing_record_get(conn, rid):
    row = conn.execute("SELECT * FROM publishing_records WHERE id = ?", (rid,)).fetchone()
    return _row_to_dict(row)


def publishing_record_list(conn, advertisement_id=None, skip=0, limit=100):
    if advertisement_id:
        rows = conn.execute(
            "SELECT * FROM publishing_records WHERE advertisement_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (advertisement_id, limit, skip),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM publishing_records ORDER BY created_at DESC LIMIT ? OFFSET ?",
                            (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def publishing_record_update(conn, rid, data):
    fields = []
    params = []
    for k, v in data.items():
        if k == "ai_disclosure_posted":
            fields.append(f"{k} = ?")
            params.append(1 if v else 0)
        else:
            fields.append(f"{k} = ?")
            params.append(v)
    if not fields:
        return publishing_record_get(conn, rid)
    params.append(rid)
    conn.execute(f"UPDATE publishing_records SET {', '.join(fields)} WHERE id = ?", params)
    return publishing_record_get(conn, rid)


def publishing_record_delete(conn, rid):
    row = publishing_record_get(conn, rid)
    if row:
        conn.execute("DELETE FROM publishing_records WHERE id = ?", (rid,))
    return row


# ===========================================================================
# Performance Metrics
# ===========================================================================
def performance_metric_create(conn, data):
    mid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO performance_metrics (id, publishing_record_id, recorded_at, views, completion_rate,
           likes, comments, shares, product_clicks, orders, cost_cny, cpa_cny, roas)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (mid, data["publishing_record_id"], data.get("recorded_at", now), data.get("views"),
         data.get("completion_rate"), data.get("likes"), data.get("comments"), data.get("shares"),
         data.get("product_clicks"), data.get("orders"), data.get("cost_cny"), data.get("cpa_cny"),
         data.get("roas")),
    )
    return performance_metric_get(conn, mid)


def performance_metric_get(conn, mid):
    row = conn.execute("SELECT * FROM performance_metrics WHERE id = ?", (mid,)).fetchone()
    return _row_to_dict(row)


def performance_metric_list(conn, publishing_record_id=None, skip=0, limit=100):
    if publishing_record_id:
        rows = conn.execute(
            "SELECT * FROM performance_metrics WHERE publishing_record_id = ? ORDER BY recorded_at DESC LIMIT ? OFFSET ?",
            (publishing_record_id, limit, skip),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM performance_metrics ORDER BY recorded_at DESC LIMIT ? OFFSET ?",
                            (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def performance_metric_update(conn, mid, data):
    fields = []
    params = []
    for k, v in data.items():
        fields.append(f"{k} = ?")
        params.append(v)
    if not fields:
        return performance_metric_get(conn, mid)
    params.append(mid)
    conn.execute(f"UPDATE performance_metrics SET {', '.join(fields)} WHERE id = ?", params)
    return performance_metric_get(conn, mid)


def performance_metric_delete(conn, mid):
    row = performance_metric_get(conn, mid)
    if row:
        conn.execute("DELETE FROM performance_metrics WHERE id = ?", (mid,))
    return row


# ===========================================================================
# Prompt Templates
# ===========================================================================
def prompt_template_create(conn, data):
    tid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO prompt_templates (id, name, agent_type, template_content, variables, version,
           is_active, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (tid, data["name"], data["agent_type"], data["template_content"], data.get("variables"),
         data.get("version", 1), 1 if data.get("is_active", True) else 0, now, now),
    )
    return prompt_template_get(conn, tid)


def prompt_template_get(conn, tid):
    row = conn.execute("SELECT * FROM prompt_templates WHERE id = ?", (tid,)).fetchone()
    return _row_to_dict(row)


def prompt_template_list(conn, agent_type=None, skip=0, limit=100):
    if agent_type:
        rows = conn.execute(
            "SELECT * FROM prompt_templates WHERE agent_type = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (agent_type, limit, skip),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM prompt_templates ORDER BY created_at DESC LIMIT ? OFFSET ?",
                            (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def prompt_template_update(conn, tid, data):
    fields = []
    params = []
    for k, v in data.items():
        if k == "is_active":
            fields.append("is_active = ?")
            params.append(1 if v else 0)
        else:
            fields.append(f"{k} = ?")
            params.append(v)
    if not fields:
        return prompt_template_get(conn, tid)
    fields.append("updated_at = ?")
    params.append(now_iso())
    params.append(tid)
    conn.execute(f"UPDATE prompt_templates SET {', '.join(fields)} WHERE id = ?", params)
    return prompt_template_get(conn, tid)


def prompt_template_delete(conn, tid):
    row = prompt_template_get(conn, tid)
    if row:
        conn.execute("DELETE FROM prompt_templates WHERE id = ?", (tid,))
    return row


# ===========================================================================
# Audit Logs
# ===========================================================================
def audit_log_create(conn, data):
    lid = generate_id()
    now = now_iso()
    conn.execute(
        """INSERT INTO audit_logs (id, user_id, action, resource_type, resource_id, details, ip_address, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (lid, data.get("user_id"), data["action"], data.get("resource_type"), data.get("resource_id"),
         data.get("details"), data.get("ip_address"), now),
    )
    return audit_log_get(conn, lid)


def audit_log_get(conn, lid):
    row = conn.execute("SELECT * FROM audit_logs WHERE id = ?", (lid,)).fetchone()
    return _row_to_dict(row)


def audit_log_list(conn, skip=0, limit=100):
    rows = conn.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ? OFFSET ?",
                        (limit, skip)).fetchall()
    return _rows_to_dicts(rows)


def audit_log_update(conn, lid, data):
    fields = []
    params = []
    for k, v in data.items():
        fields.append(f"{k} = ?")
        params.append(v)
    if not fields:
        return audit_log_get(conn, lid)
    params.append(lid)
    conn.execute(f"UPDATE audit_logs SET {', '.join(fields)} WHERE id = ?", params)
    conn.commit()
    return audit_log_get(conn, lid)
