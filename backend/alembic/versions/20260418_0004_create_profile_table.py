"""create_profile_table

Revision ID: 20260418_0004
Revises: 20260417_0003
Create Date: 2026-04-18
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260418_0004"
down_revision = "20260417_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "profile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("target_weight", sa.Float(), nullable=True),
        sa.Column("daily_calorie_target", sa.Integer(), nullable=False, server_default="2000"),
        sa.Column("protein_target", sa.Integer(), nullable=True),
        sa.Column("weekly_workout_target", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "target_weight IS NULL OR (target_weight >= 20 AND target_weight <= 500)",
            name="ck_profile_target_weight",
        ),
        sa.CheckConstraint(
            "daily_calorie_target >= 1000 AND daily_calorie_target <= 5000",
            name="ck_profile_daily_calorie_target",
        ),
        sa.CheckConstraint(
            "protein_target IS NULL OR (protein_target >= 0 AND protein_target <= 500)",
            name="ck_profile_protein_target",
        ),
        sa.CheckConstraint(
            "weekly_workout_target IS NULL OR (weekly_workout_target >= 0 AND weekly_workout_target <= 50)",
            name="ck_profile_weekly_workout_target",
        ),
    )



def downgrade() -> None:
    op.drop_table("profile")
