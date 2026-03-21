"""Initial schema.

Revision ID: 0001
Revises: None
Create Date: 2025-01-01 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # Extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Enums
    postgresql.ENUM("HUMAN", "AI_CHARACTER", name="participant_type", create_type=False).create(
        op.get_bind(), checkfirst=True
    )
    postgresql.ENUM("ONGOING", "COMPLETED", name="episode_status", create_type=False).create(
        op.get_bind(), checkfirst=True
    )

    # 1. participant
    op.create_table(
        "participant",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "type", sa.Enum("HUMAN", "AI_CHARACTER", name="participant_type"), nullable=False
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("profile", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("participant_type_idx", "participant", ["type"])

    # 2. memory_base
    op.create_table(
        "memory_base",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("participant.id"),
            nullable=False,
        ),
        sa.Column("memory_type", sa.Text(), nullable=False),
        sa.Column("importance_score", sa.Float(), nullable=False),
        sa.Column("memory_strength", sa.Float(), nullable=False),
        sa.Column("access_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "last_accessed_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.CheckConstraint("importance_score BETWEEN 0 AND 1", name="ck_memory_base_importance"),
        sa.CheckConstraint("memory_strength BETWEEN 0 AND 1", name="ck_memory_base_strength"),
    )
    op.create_index("memory_base_owner_idx", "memory_base", ["owner_id", "created_at"])
    op.create_index("memory_base_type_idx", "memory_base", ["memory_type"])
    op.create_index("memory_base_strength_idx", "memory_base", ["memory_strength"])
    op.create_index(
        "memory_base_owner_strength_idx", "memory_base", ["owner_id", "memory_strength"]
    )
    op.execute(
        "CREATE INDEX memory_base_embedding_idx ON memory_base "
        "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"
    )

    # 3. episode (before message, message has FK to episode)
    op.create_table(
        "episode",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "memory_id", sa.Integer(), sa.ForeignKey("memory_base.id"), unique=True, nullable=False
        ),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=True),
        sa.Column("turning_point", sa.Text(), nullable=True),
        sa.Column("conclusion", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("ONGOING", "COMPLETED", name="episode_status"),
            nullable=False,
            server_default="ONGOING",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("episode_memory_idx", "episode", ["memory_id"])
    op.create_index("episode_status_idx", "episode", ["status"])

    # 4. message
    op.create_table(
        "message",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "memory_id", sa.Integer(), sa.ForeignKey("memory_base.id"), unique=True, nullable=False
        ),
        sa.Column("episode_id", sa.Integer(), sa.ForeignKey("episode.id"), nullable=True),
        sa.Column(
            "sender_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("participant.id"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("message_sender_idx", "message", ["sender_id", "created_at"])
    op.create_index("message_memory_idx", "message", ["memory_id"])
    op.create_index("message_episode_idx", "message", ["episode_id", "created_at"])

    # 5. observation
    op.create_table(
        "observation",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("memory_id", sa.Integer(), sa.ForeignKey("memory_base.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("observation_memory_idx", "observation", ["memory_id"])

    # 6. reflection
    op.create_table(
        "reflection",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "memory_id", sa.Integer(), sa.ForeignKey("memory_base.id"), unique=True, nullable=False
        ),
        sa.Column(
            "parent_reflection_id", sa.Integer(), sa.ForeignKey("reflection.id"), nullable=True
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("reflection_memory_idx", "reflection", ["memory_id"])
    op.create_index("reflection_parent_idx", "reflection", ["parent_reflection_id"])

    # 7. reflection_source
    op.create_table(
        "reflection_source",
        sa.Column(
            "reflection_id",
            sa.Integer(),
            sa.ForeignKey("reflection.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "source_memory_id",
            sa.Integer(),
            sa.ForeignKey("memory_base.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_index("reflection_source_reflection_idx", "reflection_source", ["reflection_id"])
    op.create_index("reflection_source_memory_idx", "reflection_source", ["source_memory_id"])

    # 8. memory_access_log
    op.create_table(
        "memory_access_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "memory_id",
            sa.Integer(),
            sa.ForeignKey("memory_base.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("accessed_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("access_context", sa.Text(), nullable=True),
        sa.Column("retrieval_score", sa.Float(), nullable=True),
        sa.Column("reinforcement_applied", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.create_index(
        "memory_access_log_memory_idx", "memory_access_log", ["memory_id", "accessed_at"]
    )

    # 9. emotion_history
    op.create_table(
        "emotion_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "character_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("participant.id"),
            nullable=False,
        ),
        sa.Column(
            "message_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("message.id"), nullable=True
        ),
        sa.Column("joy", sa.Float(), nullable=False),
        sa.Column("sadness", sa.Float(), nullable=False),
        sa.Column("anger", sa.Float(), nullable=False),
        sa.Column("surprise", sa.Float(), nullable=False),
        sa.Column("fear", sa.Float(), nullable=False),
        sa.Column("disgust", sa.Float(), nullable=False),
        sa.Column("trigger_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("joy BETWEEN 0 AND 1", name="ck_emotion_joy"),
        sa.CheckConstraint("sadness BETWEEN 0 AND 1", name="ck_emotion_sadness"),
        sa.CheckConstraint("anger BETWEEN 0 AND 1", name="ck_emotion_anger"),
        sa.CheckConstraint("surprise BETWEEN 0 AND 1", name="ck_emotion_surprise"),
        sa.CheckConstraint("fear BETWEEN 0 AND 1", name="ck_emotion_fear"),
        sa.CheckConstraint("disgust BETWEEN 0 AND 1", name="ck_emotion_disgust"),
    )
    op.create_index(
        "emotion_history_character_idx", "emotion_history", ["character_id", "created_at"]
    )
    op.create_index("emotion_history_message_idx", "emotion_history", ["message_id"])

    # 10. character_state (after emotion_history)
    op.create_table(
        "character_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "character_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("participant.id"),
            unique=True,
            nullable=False,
        ),
        sa.Column(
            "latest_emotion_id", sa.Integer(), sa.ForeignKey("emotion_history.id"), nullable=True
        ),
        sa.Column("energy_level", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("engagement_level", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("conversation_mode", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("energy_level BETWEEN 0 AND 1", name="ck_character_state_energy"),
        sa.CheckConstraint(
            "engagement_level BETWEEN 0 AND 1", name="ck_character_state_engagement"
        ),
    )

    # 11. user_portrait
    op.create_table(
        "user_portrait",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("participant.id"),
            unique=True,
            nullable=False,
        ),
        sa.Column("personality_summary", sa.Text(), nullable=True),
        sa.Column("communication_style", sa.Text(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_updated", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("confidence_score BETWEEN 0 AND 1", name="ck_user_portrait_confidence"),
    )
    op.create_index("user_portrait_user_idx", "user_portrait", ["user_id"])

    # 12. user_trait
    op.create_table(
        "user_trait",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "portrait_id",
            sa.Integer(),
            sa.ForeignKey("user_portrait.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("trait_name", sa.Text(), nullable=False),
        sa.Column("trait_value", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("trait_value BETWEEN -1 AND 1", name="ck_user_trait_value"),
        sa.CheckConstraint("confidence BETWEEN -1 AND 1", name="ck_user_trait_confidence"),
        sa.UniqueConstraint("portrait_id", "trait_name", name="uq_user_trait"),
    )
    op.create_index("user_trait_portrait_idx", "user_trait", ["portrait_id"])

    # 13. user_interest
    op.create_table(
        "user_interest",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("participant.id"),
            nullable=False,
        ),
        sa.Column("topic", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("frequency", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("first_mentioned", sa.DateTime(), nullable=False),
        sa.Column("last_mentioned", sa.DateTime(), nullable=False),
        sa.CheckConstraint("confidence BETWEEN -1 AND 1", name="ck_user_interest_confidence"),
        sa.UniqueConstraint("user_id", "topic", name="uq_user_interest"),
    )
    op.create_index("user_interest_user_idx", "user_interest", ["user_id", "confidence"])
    op.create_index("user_interest_topic_idx", "user_interest", ["topic"])

    # 14. user_preference
    op.create_table(
        "user_preference",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("participant.id"),
            nullable=False,
        ),
        sa.Column("preference_type", sa.Text(), nullable=False),
        sa.Column("preference_value", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("confidence BETWEEN -1 AND 1", name="ck_user_preference_confidence"),
        sa.UniqueConstraint("user_id", "preference_type", name="uq_user_preference"),
    )
    op.create_index("user_preference_user_idx", "user_preference", ["user_id"])

    # 15. user_state_snapshot
    op.create_table(
        "user_state_snapshot",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("participant.id"),
            nullable=False,
        ),
        sa.Column(
            "user_portrait_id", sa.Integer(), sa.ForeignKey("user_portrait.id"), nullable=False
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(
        "user_state_snapshot_user_idx", "user_state_snapshot", ["user_id", "created_at"]
    )

    # 16. snapshot mapping tables
    op.create_table(
        "snapshot_interest",
        sa.Column(
            "snapshot_id",
            sa.Integer(),
            sa.ForeignKey("user_state_snapshot.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "interest_id",
            sa.Integer(),
            sa.ForeignKey("user_interest.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_index("snapshot_interest_interest_idx", "snapshot_interest", ["interest_id"])

    op.create_table(
        "snapshot_trait",
        sa.Column(
            "snapshot_id",
            sa.Integer(),
            sa.ForeignKey("user_state_snapshot.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "trait_id",
            sa.Integer(),
            sa.ForeignKey("user_trait.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_index("snapshot_trait_trait_idx", "snapshot_trait", ["trait_id"])

    op.create_table(
        "snapshot_preference",
        sa.Column(
            "snapshot_id",
            sa.Integer(),
            sa.ForeignKey("user_state_snapshot.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "preference_id",
            sa.Integer(),
            sa.ForeignKey("user_preference.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_index("snapshot_preference_preference_idx", "snapshot_preference", ["preference_id"])


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("snapshot_preference")
    op.drop_table("snapshot_trait")
    op.drop_table("snapshot_interest")
    op.drop_table("user_state_snapshot")
    op.drop_table("user_preference")
    op.drop_table("user_interest")
    op.drop_table("user_trait")
    op.drop_table("user_portrait")
    op.drop_table("character_state")
    op.drop_table("emotion_history")
    op.drop_table("memory_access_log")
    op.drop_table("reflection_source")
    op.drop_table("reflection")
    op.drop_table("observation")
    op.drop_table("message")
    op.drop_table("episode")
    op.drop_table("memory_base")
    op.drop_table("participant")

    op.execute("DROP INDEX IF EXISTS memory_base_embedding_idx")
    op.execute("DROP TYPE IF EXISTS episode_status")
    op.execute("DROP TYPE IF EXISTS participant_type")
    op.execute("DROP EXTENSION IF EXISTS vector")
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
