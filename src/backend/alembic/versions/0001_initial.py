"""Initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2026-11-22 11:45:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # projects
    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum("draft", "active", "completed", "archived", name="projectstatus"), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=True),
        sa.Column("budget_cny", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_name"), "projects", ["name"], unique=False)

    # customers
    op.create_table(
        "customers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("contact_person", sa.String(length=100), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=200), nullable=True),
        sa.Column("company", sa.String(length=200), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_customers_name"), "customers", ["name"], unique=False)

    # characters
    op.create_table(
        "characters",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("gender", sa.Enum("male", "female", "other", name="charactergender"), nullable=False),
        sa.Column("age_range", sa.String(length=50), nullable=True),
        sa.Column("background", sa.Text(), nullable=True),
        sa.Column("personality", sa.Text(), nullable=True),
        sa.Column("catchphrases", sa.Text(), nullable=True),
        sa.Column("worldview", sa.Text(), nullable=True),
        sa.Column("commercial_boundary", sa.Text(), nullable=True),
        sa.Column("reference_image_url", sa.String(length=500), nullable=True),
        sa.Column("voice_reference_url", sa.String(length=500), nullable=True),
        sa.Column("is_core_ip", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_characters_name"), "characters", ["name"], unique=False)

    # products
    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.Enum("home_cleaning", "daily_goods", "apparel_warmth", "other", name="productcategory"), nullable=False),
        sa.Column("price_cny", sa.Float(), nullable=True),
        sa.Column("specifications", sa.Text(), nullable=True),
        sa.Column("selling_points", sa.Text(), nullable=True),
        sa.Column("target_audience", sa.Text(), nullable=True),
        sa.Column("usage_scenarios", sa.Text(), nullable=True),
        sa.Column("proof_materials", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)
    op.create_index(op.f("ix_products_project_id"), "products", ["project_id"], unique=False)

    # character_assets
    op.create_table(
        "character_assets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("character_id", sa.String(length=36), nullable=False),
        sa.Column("asset_type", sa.String(length=50), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # story_ideas
    op.create_table(
        "story_ideas",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("story_type", sa.String(length=50), nullable=True),
        sa.Column("hook", sa.Text(), nullable=True),
        sa.Column("conflict", sa.Text(), nullable=True),
        sa.Column("twist", sa.Text(), nullable=True),
        sa.Column("product_integration", sa.Text(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("status", sa.Enum("generated", "selected", "rejected", name="storyideastatus"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_story_ideas_product_id"), "story_ideas", ["product_id"], unique=False)

    # scripts
    op.create_table(
        "scripts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("story_idea_id", sa.String(length=36), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("raw_ai_input", sa.Text(), nullable=True),
        sa.Column("raw_ai_output", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum("draft", "approved", "rejected", "in_production", name="scriptstatus"), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["story_idea_id"], ["story_ideas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scripts_story_idea_id"), "scripts", ["story_idea_id"], unique=False)

    # script_characters association
    op.create_table(
        "script_characters",
        sa.Column("script_id", sa.String(length=36), nullable=False),
        sa.Column("character_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["script_id"], ["scripts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("script_id", "character_id"),
    )

    # storyboards
    op.create_table(
        "storyboards",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("script_id", sa.String(length=36), nullable=False),
        sa.Column("shot_number", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_prompt", sa.Text(), nullable=True),
        sa.Column("dialogue", sa.Text(), nullable=True),
        sa.Column("sound_effect", sa.Text(), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["script_id"], ["scripts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_storyboards_script_id"), "storyboards", ["script_id"], unique=False)

    # production_tasks
    op.create_table(
        "production_tasks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("storyboard_id", sa.String(length=36), nullable=True),
        sa.Column("task_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.Enum("pending", "in_progress", "completed", "failed", name="taskstatus"), nullable=False),
        sa.Column("input_data", sa.Text(), nullable=True),
        sa.Column("output_data", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["storyboard_id"], ["storyboards.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # media_assets
    op.create_table(
        "media_assets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("storyboard_id", sa.String(length=36), nullable=True),
        sa.Column("production_task_id", sa.String(length=36), nullable=True),
        sa.Column("media_type", sa.Enum("image", "video", "audio", name="mediatype"), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("ai_generated", sa.Boolean(), nullable=False),
        sa.Column("ai_disclosure", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["storyboard_id"], ["storyboards.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["production_task_id"], ["production_tasks.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_media_assets_storyboard_id"), "media_assets", ["storyboard_id"], unique=False)

    # advertisements
    op.create_table(
        "advertisements",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("script_id", sa.String(length=36), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("sha256", sa.String(length=64), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("status", sa.Enum("draft", "reviewed", "published", "rejected", name="adstatus"), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("ai_disclosure", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["script_id"], ["scripts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_advertisements_project_id"), "advertisements", ["project_id"], unique=False)

    # compliance_reviews
    op.create_table(
        "compliance_reviews",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("advertisement_id", sa.String(length=36), nullable=False),
        sa.Column("reviewer_type", sa.String(length=50), nullable=False),
        sa.Column("ai_disclosure_required", sa.Boolean(), nullable=False),
        sa.Column("ai_disclosure_confirmed", sa.Boolean(), nullable=False),
        sa.Column("product_authenticity", sa.Boolean(), nullable=True),
        sa.Column("fictional_experience_check", sa.Boolean(), nullable=True),
        sa.Column("portrait_authorization", sa.Boolean(), nullable=True),
        sa.Column("voice_clone_authorization", sa.Boolean(), nullable=True),
        sa.Column("music_license", sa.Boolean(), nullable=True),
        sa.Column("trademark_check", sa.Boolean(), nullable=True),
        sa.Column("ad_content_compliance", sa.Boolean(), nullable=True),
        sa.Column("status", sa.Enum("pending", "passed", "failed", name="compliancestatus"), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["advertisement_id"], ["advertisements.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_compliance_reviews_advertisement_id"), "compliance_reviews", ["advertisement_id"], unique=False)

    # publishing_records
    op.create_table(
        "publishing_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("advertisement_id", sa.String(length=36), nullable=False),
        sa.Column("platform", sa.Enum("douyin", "other", name="publishplatform"), nullable=False),
        sa.Column("account_name", sa.String(length=200), nullable=True),
        sa.Column("publish_url", sa.String(length=500), nullable=True),
        sa.Column("publish_time", sa.DateTime(), nullable=True),
        sa.Column("ai_disclosure_posted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["advertisement_id"], ["advertisements.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_publishing_records_advertisement_id"), "publishing_records", ["advertisement_id"], unique=False)

    # performance_metrics
    op.create_table(
        "performance_metrics",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("publishing_record_id", sa.String(length=36), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.Column("views", sa.Integer(), nullable=True),
        sa.Column("completion_rate", sa.Float(), nullable=True),
        sa.Column("likes", sa.Integer(), nullable=True),
        sa.Column("comments", sa.Integer(), nullable=True),
        sa.Column("shares", sa.Integer(), nullable=True),
        sa.Column("product_clicks", sa.Integer(), nullable=True),
        sa.Column("orders", sa.Integer(), nullable=True),
        sa.Column("cost_cny", sa.Float(), nullable=True),
        sa.Column("cpa_cny", sa.Float(), nullable=True),
        sa.Column("roas", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["publishing_record_id"], ["publishing_records.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_performance_metrics_publishing_record_id"), "performance_metrics", ["publishing_record_id"], unique=False)

    # prompt_templates
    op.create_table(
        "prompt_templates",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("agent_type", sa.String(length=50), nullable=False),
        sa.Column("template_content", sa.Text(), nullable=False),
        sa.Column("variables", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_prompt_templates_name"), "prompt_templates", ["name"], unique=False)

    # audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=True),
        sa.Column("resource_id", sa.String(length=36), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_index(op.f("ix_prompt_templates_name"), table_name="prompt_templates")
    op.drop_table("prompt_templates")
    op.drop_index(op.f("ix_performance_metrics_publishing_record_id"), table_name="performance_metrics")
    op.drop_table("performance_metrics")
    op.drop_index(op.f("ix_publishing_records_advertisement_id"), table_name="publishing_records")
    op.drop_table("publishing_records")
    op.drop_index(op.f("ix_compliance_reviews_advertisement_id"), table_name="compliance_reviews")
    op.drop_table("compliance_reviews")
    op.drop_index(op.f("ix_advertisements_project_id"), table_name="advertisements")
    op.drop_table("advertisements")
    op.drop_index(op.f("ix_media_assets_storyboard_id"), table_name="media_assets")
    op.drop_table("media_assets")
    op.drop_table("production_tasks")
    op.drop_index(op.f("ix_storyboards_script_id"), table_name="storyboards")
    op.drop_table("storyboards")
    op.drop_table("script_characters")
    op.drop_index(op.f("ix_scripts_story_idea_id"), table_name="scripts")
    op.drop_table("scripts")
    op.drop_index(op.f("ix_story_ideas_product_id"), table_name="story_ideas")
    op.drop_table("story_ideas")
    op.drop_table("character_assets")
    op.drop_index(op.f("ix_products_project_id"), table_name="products")
    op.drop_index(op.f("ix_products_name"), table_name="products")
    op.drop_table("products")
    op.drop_index(op.f("ix_characters_name"), table_name="characters")
    op.drop_table("characters")
    op.drop_index(op.f("ix_customers_name"), table_name="customers")
    op.drop_table("customers")
    op.drop_index(op.f("ix_projects_name"), table_name="projects")
    op.drop_table("projects")
