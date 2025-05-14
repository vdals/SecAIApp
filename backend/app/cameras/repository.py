from typing import List, Optional, Union, Dict, Any, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.repository import BaseRepository
from app.cameras.models import Camera
from app.cameras.schemas import CameraCreate, CameraUpdate, CameraStats
from app.videos.models import Video
from app.events.models import Event


class CameraRepository(BaseRepository[Camera, CameraCreate, CameraUpdate]):
    """Camera repository"""
    
    def __init__(self):
        super().__init__(Camera)
    
    async def get_with_location(self, db: AsyncSession, *, id: int) -> Optional[Camera]:
        """Get camera with location information"""
        query = (
            select(self.model)
            .options(selectinload(self.model.location))
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_with_owner(self, db: AsyncSession, *, id: int) -> Optional[Camera]:
        """Get camera with owner information"""
        query = (
            select(self.model)
            .options(selectinload(self.model.owner))
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_full(self, db: AsyncSession, *, id: int) -> Optional[Camera]:
        """Get camera with location and owner information"""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.location),
                selectinload(self.model.owner)
            )
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_all_by_location(
        self, 
        db: AsyncSession, 
        *, 
        location_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Camera]:
        """Get all cameras for a specific location"""
        query = (
            select(self.model)
            .where(self.model.location_id == location_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_all_by_owner(
        self, 
        db: AsyncSession, 
        *, 
        owner_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Camera]:
        """Get all cameras for a specific owner"""
        query = (
            select(self.model)
            .where(self.model.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_all_with_location(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Camera]:
        """Get all cameras with location information"""
        query = (
            select(self.model)
            .options(selectinload(self.model.location))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_all_with_owner(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Camera]:
        """Get all cameras with owner information"""
        query = (
            select(self.model)
            .options(selectinload(self.model.owner))
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
    ) -> List[Camera]:
        """Get all cameras with location and owner information"""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.location),
                selectinload(self.model.owner)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_stats(self, db: AsyncSession, *, camera_id: int) -> CameraStats:
        """Get camera statistics"""
        video_query = select(func.count()).select_from(Video).where(Video.camera_id == camera_id)
        video_result = await db.execute(video_query)
        total_videos = video_result.scalar() or 0
        
        # Количество событий
        event_query = select(func.count()).select_from(Event).where(Event.camera_id == camera_id)
        event_result = await db.execute(event_query)
        total_events = event_result.scalar() or 0
        
        # Объем занятого места на диске
        disk_query = select(func.sum(Video.file_size)).select_from(Video).where(Video.camera_id == camera_id)
        disk_result = await db.execute(disk_query)
        disk_usage_bytes = disk_result.scalar() or 0
        disk_usage_mb = disk_usage_bytes / (1024 * 1024)  # Конвертация в МБ
        
        return CameraStats(
            total_videos=total_videos,
            total_events=total_events,
            disk_usage_mb=disk_usage_mb
        ) 