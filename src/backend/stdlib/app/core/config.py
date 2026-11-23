"""AI Story Commerce — Application Configuration (stdlib implementation)"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]  # 项目根目录
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
MATERIALS_DIR = DATA_DIR / "materials"
OUTPUTS_DIR = DATA_DIR / "outputs"
DATABASE_PATH = DATA_DIR / "ai_story_commerce.db"

APP_NAME = "AI Story Commerce"
APP_VERSION = "0.1.0"
DEBUG = True

# 确保数据目录存在
for _d in (DATA_DIR, UPLOAD_DIR, MATERIALS_DIR, OUTPUTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)
