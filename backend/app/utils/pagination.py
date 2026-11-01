from typing import Generic, List, TypeVar
from pydantic import BaseModel
from sqlalchemy.orm import Query

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool


def paginate_query(query: Query, skip: int = 0, limit: int = 100) -> tuple[List, int, bool]:
    """Applies limit and offset to a SQLAlchemy query and returns (items, total, has_more)."""
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    has_more = (skip + len(items)) < total
    return items, total, has_more
