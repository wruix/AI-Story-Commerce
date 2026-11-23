"""AI Story Commerce — Database layer (stdlib sqlite3 implementation)"""

import sqlite3
import os
from contextlib import contextmanager
from app.core.config import DATABASE_PATH

# Ensure database directory exists
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Schema: 16 core tables matching the SQLAlchemy design
SCHEMA = """
PRAGMA foreign_keys = ON;

-- 1. projects - 商业项目
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    customer_id TEXT,
    budget_cny REAL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);

-- 2. customers - 商家客户
CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    company TEXT,
    address TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 3. characters - 虚拟人物
CREATE TABLE IF NOT EXISTS characters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT NOT NULL,
    age_range TEXT,
    background TEXT,
    personality TEXT,
    catchphrases TEXT,
    worldview TEXT,
    commercial_boundary TEXT,
    reference_image_url TEXT,
    voice_reference_url TEXT,
    is_core_ip INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 4. products - 商品资料
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'other',
    price_cny REAL,
    specifications TEXT,
    selling_points TEXT,
    target_audience TEXT,
    usage_scenarios TEXT,
    proof_materials TEXT,
    image_url TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- 5. character_assets - 人物参考素材
CREATE TABLE IF NOT EXISTS character_assets (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    sha256 TEXT,
    description TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- 6. story_ideas - 剧情创意
CREATE TABLE IF NOT EXISTS story_ideas (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    story_type TEXT,
    hook TEXT,
    conflict TEXT,
    twist TEXT,
    product_integration TEXT,
    score REAL,
    status TEXT NOT NULL DEFAULT 'generated',
    created_at TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 7. scripts - 剧本版本
CREATE TABLE IF NOT EXISTS scripts (
    id TEXT PRIMARY KEY,
    story_idea_id TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    raw_ai_input TEXT,
    raw_ai_output TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    is_current INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY (story_idea_id) REFERENCES story_ideas(id) ON DELETE CASCADE
);

-- 8. script_characters (many-to-many association)
CREATE TABLE IF NOT EXISTS script_characters (
    script_id TEXT NOT NULL,
    character_id TEXT NOT NULL,
    PRIMARY KEY (script_id, character_id),
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE CASCADE,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- 9. storyboards - 分镜
CREATE TABLE IF NOT EXISTS storyboards (
    id TEXT PRIMARY KEY,
    script_id TEXT NOT NULL,
    shot_number INTEGER NOT NULL,
    description TEXT,
    image_prompt TEXT,
    dialogue TEXT,
    sound_effect TEXT,
    duration_seconds REAL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE CASCADE
);

-- 10. production_tasks - 视频生产任务
CREATE TABLE IF NOT EXISTS production_tasks (
    id TEXT PRIMARY KEY,
    storyboard_id TEXT,
    task_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    input_data TEXT,
    output_data TEXT,
    error_message TEXT,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (storyboard_id) REFERENCES storyboards(id) ON DELETE SET NULL
);

-- 11. media_assets - 图片、视频、音频
CREATE TABLE IF NOT EXISTS media_assets (
    id TEXT PRIMARY KEY,
    storyboard_id TEXT,
    production_task_id TEXT,
    media_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    sha256 TEXT,
    file_size_bytes INTEGER,
    duration_seconds REAL,
    width INTEGER,
    height INTEGER,
    ai_generated INTEGER NOT NULL DEFAULT 0,
    ai_disclosure INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (storyboard_id) REFERENCES storyboards(id) ON DELETE SET NULL,
    FOREIGN KEY (production_task_id) REFERENCES production_tasks(id) ON DELETE SET NULL
);

-- 12. advertisements - 广告成片
CREATE TABLE IF NOT EXISTS advertisements (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    script_id TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    title TEXT NOT NULL,
    file_path TEXT,
    sha256 TEXT,
    duration_seconds REAL,
    status TEXT NOT NULL DEFAULT 'draft',
    is_current INTEGER NOT NULL DEFAULT 1,
    ai_disclosure INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE SET NULL
);

-- 13. compliance_reviews - 合规审核
CREATE TABLE IF NOT EXISTS compliance_reviews (
    id TEXT PRIMARY KEY,
    advertisement_id TEXT NOT NULL,
    reviewer_type TEXT NOT NULL,
    ai_disclosure_required INTEGER NOT NULL DEFAULT 1,
    ai_disclosure_confirmed INTEGER NOT NULL DEFAULT 0,
    product_authenticity INTEGER,
    fictional_experience_check INTEGER,
    portrait_authorization INTEGER,
    voice_clone_authorization INTEGER,
    music_license INTEGER,
    trademark_check INTEGER,
    ad_content_compliance INTEGER,
    status TEXT NOT NULL DEFAULT 'pending',
    remarks TEXT,
    reviewed_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (advertisement_id) REFERENCES advertisements(id) ON DELETE CASCADE
);

-- 14. publishing_records - 发布记录
CREATE TABLE IF NOT EXISTS publishing_records (
    id TEXT PRIMARY KEY,
    advertisement_id TEXT NOT NULL,
    platform TEXT NOT NULL DEFAULT 'douyin',
    account_name TEXT,
    publish_url TEXT,
    publish_time TEXT,
    ai_disclosure_posted INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (advertisement_id) REFERENCES advertisements(id) ON DELETE CASCADE
);

-- 15. performance_metrics - 广告数据
CREATE TABLE IF NOT EXISTS performance_metrics (
    id TEXT PRIMARY KEY,
    publishing_record_id TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    views INTEGER,
    completion_rate REAL,
    likes INTEGER,
    comments INTEGER,
    shares INTEGER,
    product_clicks INTEGER,
    orders INTEGER,
    cost_cny REAL,
    cpa_cny REAL,
    roas REAL,
    FOREIGN KEY (publishing_record_id) REFERENCES publishing_records(id) ON DELETE CASCADE
);

-- 16. prompt_templates - AI提示词模板
CREATE TABLE IF NOT EXISTS prompt_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    agent_type TEXT NOT NULL,
    template_content TEXT NOT NULL,
    variables TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 17. audit_logs - 操作审计
CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id TEXT,
    details TEXT,
    ip_address TEXT,
    created_at TEXT NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS ix_projects_name ON projects(name);
CREATE INDEX IF NOT EXISTS ix_products_name ON products(name);
CREATE INDEX IF NOT EXISTS ix_products_project_id ON products(project_id);
CREATE INDEX IF NOT EXISTS ix_characters_name ON characters(name);
CREATE INDEX IF NOT EXISTS ix_customers_name ON customers(name);
CREATE INDEX IF NOT EXISTS ix_story_ideas_product_id ON story_ideas(product_id);
CREATE INDEX IF NOT EXISTS ix_scripts_story_idea_id ON scripts(story_idea_id);
CREATE INDEX IF NOT EXISTS ix_storyboards_script_id ON storyboards(script_id);
CREATE INDEX IF NOT EXISTS ix_media_assets_storyboard_id ON media_assets(storyboard_id);
CREATE INDEX IF NOT EXISTS ix_advertisements_project_id ON advertisements(project_id);
CREATE INDEX IF NOT EXISTS ix_compliance_reviews_ad_id ON compliance_reviews(advertisement_id);
CREATE INDEX IF NOT EXISTS ix_publishing_records_ad_id ON publishing_records(advertisement_id);
CREATE INDEX IF NOT EXISTS ix_performance_metrics_publish_id ON performance_metrics(publishing_record_id);
CREATE INDEX IF NOT EXISTS ix_prompt_templates_name ON prompt_templates(name);
"""


def get_connection():
    """Get a sqlite3 connection with row factory."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db():
    """Context manager that yields a database connection and commits/rolls back."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def generate_id():
    """Generate a UUID-like ID."""
    import uuid
    return str(uuid.uuid4())


def now_iso():
    """Current timestamp in ISO format."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
