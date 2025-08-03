from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# ✅ 匯入你的 db.metadata
from models import db

# Alembic config
config = context.config

# ✅ 根據執行環境選擇資料庫
if not os.environ.get("RENDER"):
    # 本機：使用 SQLite
    config.set_main_option("sqlalchemy.url", "sqlite:///checkin.db")
else:
    # Render 或其他雲端環境：使用環境變數 DATABASE_URL
    config.set_main_option("sqlalchemy.url", os.environ.get("DATABASE_URL"))

# 設定 logging
fileConfig(config.config_file_name)

# 目標 metadata
target_metadata = db.metadata

# OFFLINE 模式
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()

# ONLINE 模式
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# 執行
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
