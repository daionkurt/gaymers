from __future__ import annotations

import os
import uuid
from contextlib import contextmanager
from datetime import datetime
from functools import lru_cache
from typing import Any, Iterator

from sqlalchemy import DateTime, Integer, LargeBinary, String, Text, create_engine, or_, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class Member(Base):
    __tablename__ = "members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(160))
    age: Mapped[int | None] = mapped_column(Integer)
    sexuality: Mapped[str | None] = mapped_column(String(160))
    height_cm: Mapped[int | None] = mapped_column(Integer)
    location: Mapped[str | None] = mapped_column(String(200))
    favorite_color: Mapped[str | None] = mapped_column(String(120))
    favorite_food: Mapped[str | None] = mapped_column(Text)
    favorite_movies: Mapped[str | None] = mapped_column(Text)
    music_tastes: Mapped[str | None] = mapped_column(Text)
    hobbies: Mapped[str | None] = mapped_column(Text)
    zodiac_sign: Mapped[str | None] = mapped_column(String(120))
    favorite_character: Mapped[str | None] = mapped_column(Text)
    gaming_system: Mapped[str | None] = mapped_column(String(160))
    currently_playing: Mapped[str | None] = mapped_column(Text)
    instagram: Mapped[str | None] = mapped_column(String(160))
    birthday: Mapped[str | None] = mapped_column(String(120))
    photo_bytes: Mapped[bytes | None] = mapped_column(LargeBinary)
    photo_mime_type: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


TEXT_FIELDS = [
    "full_name",
    "nickname",
    "sexuality",
    "location",
    "favorite_color",
    "favorite_food",
    "favorite_movies",
    "music_tastes",
    "hobbies",
    "zodiac_sign",
    "favorite_character",
    "gaming_system",
    "currently_playing",
    "instagram",
    "birthday",
    "photo_mime_type",
]

INTEGER_FIELDS = ["age", "height_cm"]


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url


def resolve_database_url() -> str:
    env_value = os.getenv("DATABASE_URL")
    if env_value:
        return _normalize_database_url(env_value)

    try:
        import streamlit as st

        secret_value = st.secrets.get("DATABASE_URL")
        if secret_value:
            return _normalize_database_url(secret_value)
    except Exception:
        pass

    return "sqlite:///group_members.db"


def get_database_backend() -> str:
    database_url = resolve_database_url()
    if database_url.startswith("sqlite"):
        return "SQLite local"
    if database_url.startswith("postgresql"):
        return "PostgreSQL"
    return "Base externa"


@lru_cache(maxsize=1)
def get_engine():
    database_url = resolve_database_url()
    engine_kwargs: dict[str, Any] = {"future": True}

    if database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs["pool_pre_ping"] = True

    return create_engine(database_url, **engine_kwargs)


@lru_cache(maxsize=1)
def get_session_factory():
    return sessionmaker(bind=get_engine(), expire_on_commit=False, class_=Session)


@contextmanager
def session_scope() -> Iterator[Session]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    Base.metadata.create_all(get_engine())


def _sanitize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _prepare_member_payload(data: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}

    for field in TEXT_FIELDS:
        payload[field] = _sanitize_text(data.get(field))

    for field in INTEGER_FIELDS:
        value = data.get(field)
        payload[field] = value if value not in ("", None) else None

    payload["photo_bytes"] = data.get("photo_bytes")
    return payload


def _member_to_dict(member: Member) -> dict[str, Any]:
    photo_bytes = bytes(member.photo_bytes) if member.photo_bytes is not None else None
    return {
        "id": member.id,
        "full_name": member.full_name,
        "nickname": member.nickname,
        "age": member.age,
        "sexuality": member.sexuality,
        "height_cm": member.height_cm,
        "location": member.location,
        "favorite_color": member.favorite_color,
        "favorite_food": member.favorite_food,
        "favorite_movies": member.favorite_movies,
        "music_tastes": member.music_tastes,
        "hobbies": member.hobbies,
        "zodiac_sign": member.zodiac_sign,
        "favorite_character": member.favorite_character,
        "gaming_system": member.gaming_system,
        "currently_playing": member.currently_playing,
        "instagram": member.instagram,
        "birthday": member.birthday,
        "photo_bytes": photo_bytes,
        "photo_mime_type": member.photo_mime_type,
        "has_photo": photo_bytes is not None,
        "created_at": member.created_at,
        "updated_at": member.updated_at,
    }


def list_members(search: str = "") -> list[dict[str, Any]]:
    with session_scope() as session:
        stmt = select(Member)

        if search.strip():
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Member.full_name.ilike(pattern),
                    Member.nickname.ilike(pattern),
                    Member.location.ilike(pattern),
                    Member.music_tastes.ilike(pattern),
                    Member.gaming_system.ilike(pattern),
                    Member.currently_playing.ilike(pattern),
                    Member.favorite_food.ilike(pattern),
                    Member.favorite_movies.ilike(pattern),
                    Member.hobbies.ilike(pattern),
                )
            )

        stmt = stmt.order_by(Member.full_name.asc())
        members = session.scalars(stmt).all()
        return [_member_to_dict(member) for member in members]


def get_member(member_id: str) -> dict[str, Any] | None:
    with session_scope() as session:
        member = session.get(Member, member_id)
        if member is None:
            return None
        return _member_to_dict(member)


def create_member(data: dict[str, Any]) -> dict[str, Any]:
    payload = _prepare_member_payload(data)
    member = Member(id=str(uuid.uuid4()), **payload)

    with session_scope() as session:
        session.add(member)
        session.flush()
        session.refresh(member)
        return _member_to_dict(member)


def update_member(member_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    payload = _prepare_member_payload(data)

    with session_scope() as session:
        member = session.get(Member, member_id)
        if member is None:
            return None

        for field, value in payload.items():
            setattr(member, field, value)

        member.updated_at = datetime.utcnow()
        session.add(member)
        session.flush()
        session.refresh(member)
        return _member_to_dict(member)


def delete_member(member_id: str) -> bool:
    with session_scope() as session:
        member = session.get(Member, member_id)
        if member is None:
            return False

        session.delete(member)
        return True
