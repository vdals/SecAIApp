from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from sqlalchemy import select, func, between
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi.encoders import jsonable_encoder

from app.common.repository import BaseRepository
from app.videos.models import Video
from app.videos.schemas import VideoCreate, VideoUpdate


class VideoRepository(BaseRepository[Video, VideoCreate, VideoUpdate]):
    """Repository for working with videos"""
    
    def __init__(self):
        super().__init__(Video)
    
    async def create(self, db: AsyncSession, *, obj_in: VideoCreate) -> Video:
        """
        Create a new video record, correctly handling dates
        """
        obj_in_data = obj_in.model_dump()
        
        if obj_in_data.get('recording_start') and obj_in_data['recording_start'].tzinfo:
            obj_in_data['recording_start'] = obj_in_data['recording_start'].replace(tzinfo=None)
            
        if obj_in_data.get('recording_end') and obj_in_data['recording_end'].tzinfo:
            obj_in_data['recording_end'] = obj_in_data['recording_end'].replace(tzinfo=None)

        db_obj = self.model(**obj_in_data)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_with_camera(self, db: AsyncSession, *, id: int) -> Optional[Video]:
        """Get video with camera information"""
        query = (
            select(self.model)
            .options(selectinload(self.model.camera))
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_with_events(self, db: AsyncSession, *, id: int) -> Optional[Video]:
        """Get video with events information"""
        query = (
            select(self.model)
            .options(selectinload(self.model.events))
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_full(self, db: AsyncSession, *, id: int) -> Optional[Video]:
        """Get video with camera and events information"""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.camera),
                selectinload(self.model.events)
            )
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_all_by_camera(
        self, 
        db: AsyncSession, 
        *, 
        camera_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Video]:
        """Get all videos for a specific camera"""
        query = (
            select(self.model)
            .where(self.model.camera_id == camera_id)
            .order_by(self.model.recording_start.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_date_range(
        self, 
        db: AsyncSession, 
        *, 
        start_date: datetime, 
        end_date: datetime, 
        camera_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Video]:
        """Get videos for a specific date range"""
        if start_date.tzinfo:
            start_date = start_date.replace(tzinfo=None)
        if end_date.tzinfo:
            end_date = end_date.replace(tzinfo=None)
            
        query = select(self.model)
        
        query = query.where(
            between(self.model.recording_start, start_date, end_date) |
            between(self.model.recording_end, start_date, end_date) |
            ((self.model.recording_start <= start_date) & (self.model.recording_end >= end_date))
        )
        
        if camera_id is not None:
            query = query.where(self.model.camera_id == camera_id)
        
        query = (
            query
            .order_by(self.model.recording_start.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count_by_camera(self, db: AsyncSession, *, camera_id: int) -> int:
        """Count the number of videos for a specific camera"""
        query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.camera_id == camera_id)
        )
        result = await db.execute(query)
        return result.scalar()
    
    async def count_by_date_range(
        self, 
        db: AsyncSession, 
        *, 
        start_date: datetime, 
        end_date: datetime, 
        camera_id: Optional[int] = None
    ) -> int:
        """Count the number of videos for a specific date range"""
        if start_date.tzinfo:
            start_date = start_date.replace(tzinfo=None)
        if end_date.tzinfo:
            end_date = end_date.replace(tzinfo=None)
            
        query = select(func.count()).select_from(self.model)
        
        query = query.where(
            between(self.model.recording_start, start_date, end_date) |
            between(self.model.recording_end, start_date, end_date) |
            ((self.model.recording_start <= start_date) & (self.model.recording_end >= end_date))
        )
        
        if camera_id is not None:
            query = query.where(self.model.camera_id == camera_id)
        
        result = await db.execute(query)
        return result.scalar()
    
    async def get_total_size_by_camera(self, db: AsyncSession, *, camera_id: int) -> int:
        """Get the total size of videos for a specific camera"""
        query = (
            select(func.sum(self.model.file_size))
            .select_from(self.model)
            .where(self.model.camera_id == camera_id)
        )
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def get_latest_by_camera(
        self, 
        db: AsyncSession, 
        *, 
        camera_id: int, 
        limit: int = 5
    ) -> List[Video]:
        """Get the latest videos for a specific camera"""
        query = (
            select(self.model)
            .where(self.model.camera_id == camera_id)
            .order_by(self.model.recording_start.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_processing_status(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        status: str
    ) -> Optional[Video]:
        """Update the processing status of a video"""
        video = await self.get(db, id=id)
        if not video:
            return None
        
        video.processing_status = status
        video.updated_at = datetime.utcnow()
        
        if status == "completed":
            video.is_processed = True
        
        db.add(video)
        await db.commit()
        await db.refresh(video)
        return video
    
    async def update_analysis_status(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        is_analyzed: bool
    ) -> Optional[Video]:
        """Update the analysis status of a video"""
        video = await self.get(db, id=id)
        if not video:
            return None
        
        video.is_analyzed = is_analyzed
        video.updated_at = datetime.utcnow()
        
        db.add(video)
        await db.commit()
        await db.refresh(video)
        return video 