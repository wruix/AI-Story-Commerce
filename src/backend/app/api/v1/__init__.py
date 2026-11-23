"""API v1 routers for all resources"""

from fastapi import APIRouter

from app.api.v1 import (
    projects, customers, products, characters,
    story_ideas, scripts, storyboards, production_tasks,
    media_assets, advertisements, compliance_reviews,
    publishing_records, performance_metrics, prompt_templates,
    audit_logs, health,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(characters.router, prefix="/characters", tags=["characters"])
api_router.include_router(story_ideas.router, prefix="/story-ideas", tags=["story-ideas"])
api_router.include_router(scripts.router, prefix="/scripts", tags=["scripts"])
api_router.include_router(storyboards.router, prefix="/storyboards", tags=["storyboards"])
api_router.include_router(production_tasks.router, prefix="/production-tasks", tags=["production-tasks"])
api_router.include_router(media_assets.router, prefix="/media-assets", tags=["media-assets"])
api_router.include_router(advertisements.router, prefix="/advertisements", tags=["advertisements"])
api_router.include_router(compliance_reviews.router, prefix="/compliance-reviews", tags=["compliance-reviews"])
api_router.include_router(publishing_records.router, prefix="/publishing-records", tags=["publishing-records"])
api_router.include_router(performance_metrics.router, prefix="/performance-metrics", tags=["performance-metrics"])
api_router.include_router(prompt_templates.router, prefix="/prompt-templates", tags=["prompt-templates"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])
