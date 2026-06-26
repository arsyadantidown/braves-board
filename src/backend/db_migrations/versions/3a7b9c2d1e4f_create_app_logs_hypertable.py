"""create app_logs hypertable with retention and compression policies

Revision ID: 3a7b9c2d1e4f
Revises: 1097929dc4bb
Create Date: 2026-06-25 09:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a7b9c2d1e4f'
down_revision: Union[str, None] = '1097929dc4bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Enable TimescaleDB extension
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")

    # Step 2: Create app_logs table
    op.execute("""
        CREATE TABLE IF NOT EXISTS app_logs (
            id              BIGSERIAL,
            timestamp       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            log_type        VARCHAR(20)     NOT NULL,
            level           VARCHAR(10)     NOT NULL,
            logger_name     VARCHAR(255)    NOT NULL,
            message         TEXT            NOT NULL,
            user_id         UUID            NULL,
            request_id      VARCHAR(64)     NULL,
            method          VARCHAR(10)     NULL,
            path            VARCHAR(512)    NULL,
            status_code     INTEGER         NULL,
            duration_ms     DOUBLE PRECISION NULL,
            ip_address      VARCHAR(45)     NULL,
            user_agent      TEXT            NULL,
            action          VARCHAR(100)    NULL,
            resource_type   VARCHAR(50)     NULL,
            resource_id     VARCHAR(64)     NULL,
            extra           JSONB           NULL,
            PRIMARY KEY (id, timestamp)
        );
    """)

    # Step 3: Convert to hypertable (partition by timestamp, 1 day chunks)
    op.execute(
        "SELECT create_hypertable('app_logs', 'timestamp', "
        "chunk_time_interval => INTERVAL '1 day');"
    )

    # Step 4: Create indexes for common query patterns
    op.execute(
        "CREATE INDEX idx_app_logs_log_type ON app_logs (log_type, timestamp DESC);"
    )
    op.execute(
        "CREATE INDEX idx_app_logs_level ON app_logs (level, timestamp DESC);"
    )
    op.execute(
        "CREATE INDEX idx_app_logs_user ON app_logs (user_id, timestamp DESC) "
        "WHERE user_id IS NOT NULL;"
    )
    op.execute(
        "CREATE INDEX idx_app_logs_request ON app_logs (request_id, timestamp DESC) "
        "WHERE request_id IS NOT NULL;"
    )
    op.execute(
        "CREATE INDEX idx_app_logs_action ON app_logs (action, timestamp DESC) "
        "WHERE action IS NOT NULL;"
    )

    # Step 5: Enable compression and set compression policy (compress chunks > 7 days)
    op.execute("""
        ALTER TABLE app_logs SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'log_type, level',
            timescaledb.compress_orderby = 'timestamp DESC'
        );
    """)
    op.execute("SELECT add_compression_policy('app_logs', INTERVAL '7 days');")

    # Step 6: Set retention policy (drop chunks > 30 days)
    op.execute("SELECT add_retention_policy('app_logs', INTERVAL '30 days');")


def downgrade() -> None:
    # Remove policies before dropping table
    op.execute("SELECT remove_retention_policy('app_logs', if_exists => true);")
    op.execute("SELECT remove_compression_policy('app_logs', if_exists => true);")
    op.execute("DROP TABLE IF EXISTS app_logs;")
