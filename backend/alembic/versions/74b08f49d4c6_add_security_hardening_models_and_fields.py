"""Add security hardening models and fields

Revision ID: 74b08f49d4c6
Revises: b318c97515a6
Create Date: 2026-01-08 16:33:17.845560

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "74b08f49d4c6"
down_revision: Union[str, Sequence[str], None] = "b318c97515a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create email_preferences table if not exists
    op.create_table(
        "email_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("weekly_digest_enabled", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("session_reports_enabled", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("unsubscribe_token", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("unsubscribe_token"),
        sqlite_autoincrement=True,
    )
    op.create_index(op.f("ix_email_preferences_email"), "email_preferences", ["email"], unique=True)

    # Create email_send_logs table
    op.create_table(
        "email_send_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("email_type", sa.String(length=50), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=True),
        sa.Column("week_start_date", sa.Date(), nullable=True),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
        sqlite_autoincrement=True,
    )
    op.create_index(op.f("ix_email_send_logs_email"), "email_send_logs", ["email"], unique=False)
    op.create_index(
        op.f("ix_email_send_logs_email_type"), "email_send_logs", ["email_type"], unique=False
    )
    op.create_index(
        op.f("ix_email_send_logs_session_id"), "email_send_logs", ["session_id"], unique=False
    )
    op.create_index(
        op.f("ix_email_send_logs_week_start_date"),
        "email_send_logs",
        ["week_start_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_email_send_logs_idempotency_key"),
        "email_send_logs",
        ["idempotency_key"],
        unique=True,
    )
    op.create_index(
        "idx_email_type_status", "email_send_logs", ["email", "email_type", "status"], unique=False
    )

    # Create email_throttles table
    op.create_table(
        "email_throttles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("email_type", sa.String(length=50), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("send_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_send_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sqlite_autoincrement=True,
    )
    op.create_index(
        "idx_email_throttle_lookup",
        "email_throttles",
        ["email", "email_type", "window_start"],
        unique=False,
    )

    # Add session_access_token to hint_sessions table
    with op.batch_alter_table("hint_sessions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("session_access_token", sa.String(length=36), nullable=True))
        batch_op.create_index(
            "ix_hint_sessions_session_access_token", ["session_access_token"], unique=False
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop session_access_token from hint_sessions
    with op.batch_alter_table("hint_sessions", schema=None) as batch_op:
        batch_op.drop_index("ix_hint_sessions_session_access_token")
        batch_op.drop_column("session_access_token")

    # Drop email_throttles table
    op.drop_index("idx_email_throttle_lookup", table_name="email_throttles")
    op.drop_table("email_throttles")

    # Drop email_send_logs table
    op.drop_index("idx_email_type_status", table_name="email_send_logs")
    op.drop_index(op.f("ix_email_send_logs_idempotency_key"), table_name="email_send_logs")
    op.drop_index(op.f("ix_email_send_logs_week_start_date"), table_name="email_send_logs")
    op.drop_index(op.f("ix_email_send_logs_session_id"), table_name="email_send_logs")
    op.drop_index(op.f("ix_email_send_logs_email_type"), table_name="email_send_logs")
    op.drop_index(op.f("ix_email_send_logs_email"), table_name="email_send_logs")
    op.drop_table("email_send_logs")

    # Drop email_preferences table
    op.drop_index(op.f("ix_email_preferences_email"), table_name="email_preferences")
    op.drop_table("email_preferences")
