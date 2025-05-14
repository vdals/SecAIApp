from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base import BaseDBModel

ModelType = TypeVar("ModelType", bound=BaseDBModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUD repository base class
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Get by ID
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_attribute(self, db: AsyncSession, attr_name: str, attr_value: Any) -> Optional[ModelType]:
        """
        Get by attribute
        """
        query = select(self.model).where(getattr(self.model, attr_name) == attr_value)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_with_related(self, db: AsyncSession, id: Any, related_fields: List[str]) -> Optional[ModelType]:
        """
        Get by ID with related entities
        """
        query = select(self.model).where(self.model.id == id)
        for field in related_fields:
            query = query.options(selectinload(getattr(self.model, field)))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_all(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get all with optional filtering
        """
        query = select(self.model)
        
        if filters:
            for attr_name, attr_value in filters.items():
                if hasattr(self.model, attr_name):
                    query = query.where(getattr(self.model, attr_name) == attr_value)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def count(self, db: AsyncSession, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filtering
        """
        query = select(func.count()).select_from(self.model)
        
        if filters:
            for attr_name, attr_value in filters.items():
                if hasattr(self.model, attr_name):
                    query = query.where(getattr(self.model, attr_name) == attr_value)
        
        result = await db.execute(query)
        return result.scalar()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create new record
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: ModelType, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update record
        """
        from datetime import datetime
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        for field in update_data:
            if hasattr(db_obj, field):
                value = update_data[field]
                if isinstance(value, datetime) and value.tzinfo:
                    value = value.replace(tzinfo=None)
                setattr(db_obj, field, value)
                
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_by_id(
        self, 
        db: AsyncSession, 
        *, 
        id: Any, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """
        Update by ID
        """
        from datetime import datetime
        
        if isinstance(obj_in, dict):
            update_data = obj_in.copy()
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if isinstance(value, datetime) and value.tzinfo:
                update_data[field] = value.replace(tzinfo=None)
            
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        
        await db.execute(query)
        await db.commit()
        return await self.get(db=db, id=id)

    async def delete(self, db: AsyncSession, *, id: Any) -> bool:
        """
        Delete record
        """
        query = delete(self.model).where(self.model.id == id)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0 