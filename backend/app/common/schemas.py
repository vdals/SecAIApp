from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base Pydantic model with configuration"""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class IdSchema(BaseSchema):
    """Schema with ID field"""
    id: int


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields"""
    created_at: datetime
    updated_at: datetime


class BaseSchemaWithId(IdSchema, TimestampSchema):
    """Schema with ID and timestamps"""
    pass


class PaginationParams(BaseSchema):
    """Query parameters for pagination"""
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


T = TypeVar('T')


class PaginatedResult(BaseSchema, Generic[T]):
    """Paginated response with items and metadata"""
    items: List[T]
    total: int
    skip: int
    limit: int
    
    @classmethod
    def create(cls, items: List[T], total: int, skip: int, limit: int):
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        ) 