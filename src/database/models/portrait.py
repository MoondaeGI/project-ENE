"""User understanding ORM models: UserPortrait, UserTrait, UserInterest, UserPreference, Snapshots."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base

if TYPE_CHECKING:
    from database.models.participant import Participant


class UserPortrait(Base):
    """사용자 전체 프로필 테이블."""

    __tablename__ = "user_portrait"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participant.id"), unique=True, nullable=False
    )
    personality_summary: Mapped[str | None] = mapped_column(Text)
    communication_style: Mapped[str | None] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped[Participant] = relationship("Participant", back_populates="user_portrait")
    traits: Mapped[list[UserTrait]] = relationship(
        "UserTrait", back_populates="portrait", cascade="all, delete-orphan"
    )
    state_snapshots: Mapped[list[UserStateSnapshot]] = relationship(
        "UserStateSnapshot", back_populates="user_portrait"
    )

    __table_args__ = (
        CheckConstraint("confidence_score BETWEEN 0 AND 1", name="ck_user_portrait_confidence"),
        Index("user_portrait_user_idx", "user_id"),
    )


class UserTrait(Base):
    """사용자 성격 특성 테이블."""

    __tablename__ = "user_trait"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    portrait_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_portrait.id", ondelete="CASCADE"), nullable=False
    )
    trait_name: Mapped[str] = mapped_column(Text, nullable=False)
    trait_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    portrait: Mapped[UserPortrait] = relationship("UserPortrait", back_populates="traits")
    snapshot_traits: Mapped[list[SnapshotTrait]] = relationship(
        "SnapshotTrait", back_populates="trait"
    )

    __table_args__ = (
        CheckConstraint("trait_value BETWEEN -1 AND 1", name="ck_user_trait_value"),
        CheckConstraint("confidence BETWEEN -1 AND 1", name="ck_user_trait_confidence"),
        UniqueConstraint("portrait_id", "trait_name", name="uq_user_trait"),
        Index("user_trait_portrait_idx", "portrait_id"),
    )


class UserInterest(Base):
    """사용자 관심사 테이블."""

    __tablename__ = "user_interest"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participant.id"), nullable=False
    )
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)  # -1(기피) ~ 1(관심)
    frequency: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    first_mentioned: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_mentioned: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships
    user: Mapped[Participant] = relationship("Participant", back_populates="user_interests")
    snapshot_interests: Mapped[list[SnapshotInterest]] = relationship(
        "SnapshotInterest", back_populates="interest"
    )

    __table_args__ = (
        CheckConstraint("confidence BETWEEN -1 AND 1", name="ck_user_interest_confidence"),
        UniqueConstraint("user_id", "topic", name="uq_user_interest"),
        Index("user_interest_user_idx", "user_id", "confidence"),
        Index("user_interest_topic_idx", "topic"),
    )


class UserPreference(Base):
    """사용자 선호도 테이블."""

    __tablename__ = "user_preference"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participant.id"), nullable=False
    )
    preference_type: Mapped[str] = mapped_column(Text, nullable=False)
    preference_value: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped[Participant] = relationship("Participant", back_populates="user_preferences")
    snapshot_preferences: Mapped[list[SnapshotPreference]] = relationship(
        "SnapshotPreference", back_populates="preference"
    )

    __table_args__ = (
        CheckConstraint("confidence BETWEEN -1 AND 1", name="ck_user_preference_confidence"),
        UniqueConstraint("user_id", "preference_type", name="uq_user_preference"),
        Index("user_preference_user_idx", "user_id"),
    )


class UserStateSnapshot(Base):
    """특정 시점의 사용자 상태 스냅샷 테이블."""

    __tablename__ = "user_state_snapshot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participant.id"), nullable=False
    )
    user_portrait_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_portrait.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped[Participant] = relationship("Participant", back_populates="user_state_snapshots")
    user_portrait: Mapped[UserPortrait] = relationship(
        "UserPortrait", back_populates="state_snapshots"
    )
    snapshot_interests: Mapped[list[SnapshotInterest]] = relationship(
        "SnapshotInterest", back_populates="snapshot"
    )
    snapshot_traits: Mapped[list[SnapshotTrait]] = relationship(
        "SnapshotTrait", back_populates="snapshot"
    )
    snapshot_preferences: Mapped[list[SnapshotPreference]] = relationship(
        "SnapshotPreference", back_populates="snapshot"
    )

    __table_args__ = (Index("user_state_snapshot_user_idx", "user_id", "created_at"),)


class SnapshotInterest(Base):
    """스냅샷-관심사 연결 테이블."""

    __tablename__ = "snapshot_interest"

    snapshot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_state_snapshot.id", ondelete="CASCADE"), primary_key=True
    )
    interest_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_interest.id", ondelete="CASCADE"), primary_key=True
    )

    snapshot: Mapped[UserStateSnapshot] = relationship(
        "UserStateSnapshot", back_populates="snapshot_interests"
    )
    interest: Mapped[UserInterest] = relationship(
        "UserInterest", back_populates="snapshot_interests"
    )

    __table_args__ = (Index("snapshot_interest_interest_idx", "interest_id"),)


class SnapshotTrait(Base):
    """스냅샷-특성 연결 테이블."""

    __tablename__ = "snapshot_trait"

    snapshot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_state_snapshot.id", ondelete="CASCADE"), primary_key=True
    )
    trait_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_trait.id", ondelete="CASCADE"), primary_key=True
    )

    snapshot: Mapped[UserStateSnapshot] = relationship(
        "UserStateSnapshot", back_populates="snapshot_traits"
    )
    trait: Mapped[UserTrait] = relationship("UserTrait", back_populates="snapshot_traits")

    __table_args__ = (Index("snapshot_trait_trait_idx", "trait_id"),)


class SnapshotPreference(Base):
    """스냅샷-선호도 연결 테이블."""

    __tablename__ = "snapshot_preference"

    snapshot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_state_snapshot.id", ondelete="CASCADE"), primary_key=True
    )
    preference_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_preference.id", ondelete="CASCADE"), primary_key=True
    )

    snapshot: Mapped[UserStateSnapshot] = relationship(
        "UserStateSnapshot", back_populates="snapshot_preferences"
    )
    preference: Mapped[UserPreference] = relationship(
        "UserPreference", back_populates="snapshot_preferences"
    )

    __table_args__ = (Index("snapshot_preference_preference_idx", "preference_id"),)
