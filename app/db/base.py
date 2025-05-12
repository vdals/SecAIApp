from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models"""
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class TimestampMixin:
    """Mixin for adding created_at and updated_at fields"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BaseDBModel(Base):
    """Base model with ID and timestamps"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, **kwargs):
        """
        Safe constructor, filtering invalid arguments
        """
        kwargs.pop('args', None)
        kwargs.pop('kwargs', None)
        super().__init__(**kwargs)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Any:
        """Create an instance from a dictionary"""
        valid_data = {k: v for k, v in data.items() if k not in ['args', 'kwargs']}
        return cls(**valid_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary"""
        return {column.name: getattr(self, column.name) 
                for column in self.__table__.columns} 