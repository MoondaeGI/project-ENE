"""Repository 패키지"""
from repositories.base import BaseRepository
from repositories.person_repository import PersonRepository

__all__ = [
    "BaseRepository",
    "PersonRepository",
]

