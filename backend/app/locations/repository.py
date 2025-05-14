from typing import List, Optional, Union, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.repository import BaseRepository
from app.locations.models import Location
from app.locations.schemas import LocationCreate, LocationUpdate


class LocationRepository(BaseRepository[Location, LocationCreate, LocationUpdate]):
    """Repository for working with locations"""
    
    def __init__(self):
        super().__init__(Location)
    
    async def get_with_users(self, db: AsyncSession, *, id: int) -> Optional[Location]:
        """Get location with users"""
        query = (
            select(self.model)
            .options(selectinload(self.model.users))
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_with_cameras(self, db: AsyncSession, *, id: int) -> Optional[Location]:
        """Get location with cameras"""
        query = (
            select(self.model)
            .options(selectinload(self.model.cameras))
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_full(self, db: AsyncSession, *, id: int) -> Optional[Location]:
        """Get location with users and cameras"""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.users),
                selectinload(self.model.cameras)
            )
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_all_with_users(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Location]:
        """Get all locations with users"""
        query = (
            select(self.model)
            .options(selectinload(self.model.users))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_all_with_cameras(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Location]:
        """Get all locations with cameras"""
        query = (
            select(self.model)
            .options(selectinload(self.model.cameras))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_all_full(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Location]:
        """Get all locations with users and cameras"""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.users),
                selectinload(self.model.cameras)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Location]:
        """Get location by name"""
        query = select(self.model).where(self.model.name == name)
        result = await db.execute(query)
        return result.scalars().first() 