"""Timezone-aware timestamps + field length constraints.

Revision ID: 20260415_0002
Revises: 20260409_0001
Create Date: 2026-04-15
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260415_0002"
down_revision = "20260409_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("health_records") as batch:
        batch.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
        )
        batch.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
        )
        batch.alter_column(
            "exercise_type",
            existing_type=sa.String(length=100),
            type_=sa.String(length=50),
            existing_nullable=True,
        )
        batch.alter_column(
            "note",
            existing_type=sa.String(),
            type_=sa.String(length=500),
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("health_records") as batch:
        batch.alter_column(
            "note",
            existing_type=sa.String(length=500),
            type_=sa.String(),
            existing_nullable=True,
        )
        batch.alter_column(
            "exercise_type",
            existing_type=sa.String(length=50),
            type_=sa.String(length=100),
            existing_nullable=True,
        )
        batch.alter_column(
            "updated_at",
            existing_type=sa.DateTime(timezone=True),
            type_=sa.DateTime(),
            existing_nullable=False,
        )
        batch.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            type_=sa.DateTime(),
            existing_nullable=False,
        )

