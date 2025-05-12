from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union, Tuple

from sqlalchemy import select, func, desc, and_, or_, between
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.repository import BaseRepository
from app.events.models import Event, Object
from app.events.schemas import (
    EventCreate, EventUpdate, ObjectCreate, ObjectUpdate, EventStats
)


class ObjectRepository(BaseRepository[Object, ObjectCreate, ObjectUpdate]):
    """Репозиторий для работы с объектами"""
    
    def __init__(self):
        super().__init__(Object)
    
    async def get_all_by_event(
        self, 
        db: AsyncSession, 
        *, 
        event_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Object]:
        """Получение всех объектов для конкретного события"""
        query = (
            select(self.model)
            .where(self.model.event_id == event_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count_by_event(self, db: AsyncSession, *, event_id: int) -> int:
        """Подсчет количества объектов для конкретного события"""
        query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.event_id == event_id)
        )
        result = await db.execute(query)
        return result.scalar()
    
    async def count_by_type(self, db: AsyncSession, *, object_type: str) -> int:
        """Подсчет количества объектов определенного типа"""
        query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.object_type == object_type)
        )
        result = await db.execute(query)
        return result.scalar()
    
    async def get_object_types_stats(self, db: AsyncSession) -> Dict[str, int]:
        """Получение статистики по типам объектов"""
        query = (
            select(self.model.object_type, func.count())
            .group_by(self.model.object_type)
        )
        result = await db.execute(query)
        return {row[0]: row[1] for row in result.all()}


class EventRepository(BaseRepository[Event, EventCreate, EventUpdate]):
    """Репозиторий для работы с событиями"""
    
    def __init__(self):
        super().__init__(Event)
    
    async def get_with_objects(self, db: AsyncSession, *, id: int) -> Optional[Event]:
        """Получение события с объектами"""
        query = (
            select(self.model)
            .options(selectinload(self.model.objects))
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_with_camera(self, db: AsyncSession, *, id: int) -> Optional[Event]:
        """Получение события с камерой"""
        query = (
            select(self.model)
            .options(selectinload(self.model.camera))
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_with_video(self, db: AsyncSession, *, id: int) -> Optional[Event]:
        """Получение события с видео"""
        query = (
            select(self.model)
            .options(selectinload(self.model.video))
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_full(self, db: AsyncSession, *, id: int) -> Optional[Event]:
        """Получение события со всеми связями"""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.objects),
                selectinload(self.model.camera),
                selectinload(self.model.video)
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
    ) -> List[Event]:
        """Получение всех событий для конкретной камеры"""
        query = (
            select(self.model)
            .where(self.model.camera_id == camera_id)
            .order_by(desc(self.model.timestamp))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_all_by_video(
        self, 
        db: AsyncSession, 
        *, 
        video_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Event]:
        """Получение всех событий для конкретного видео"""
        query = (
            select(self.model)
            .where(self.model.video_id == video_id)
            .order_by(desc(self.model.timestamp))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_all_by_type(
        self, 
        db: AsyncSession, 
        *, 
        event_type: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Event]:
        """Получение всех событий определенного типа"""
        query = (
            select(self.model)
            .where(self.model.event_type == event_type)
            .order_by(desc(self.model.timestamp))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_all_by_date_range(
        self, 
        db: AsyncSession, 
        *, 
        start_date: datetime, 
        end_date: datetime, 
        camera_id: Optional[int] = None,
        event_type: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Event]:
        """Get events for a specific period"""
        # Convert timezone-aware datetime to timezone-naive if necessary
        if start_date.tzinfo:
            start_date = start_date.replace(tzinfo=None)
        if end_date.tzinfo:
            end_date = end_date.replace(tzinfo=None)
            
        query = select(self.model)
        
        query = query.where(between(self.model.timestamp, start_date, end_date))
        
        if camera_id is not None:
            query = query.where(self.model.camera_id == camera_id)
        
        if event_type is not None:
            query = query.where(self.model.event_type == event_type)
        
        query = (
            query
            .order_by(self.model.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count_by_camera(self, db: AsyncSession, *, camera_id: int) -> int:
        """Count events for a specific camera"""
        query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.camera_id == camera_id)
        )
        result = await db.execute(query)
        return result.scalar()
    
    async def count_by_video(self, db: AsyncSession, *, video_id: int) -> int:
        """Count events for a specific video"""
        query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.video_id == video_id)
        )
        result = await db.execute(query)
        return result.scalar()
    
    async def count_by_type(self, db: AsyncSession, *, event_type: str) -> int:
        """Count events of a specific type"""
        query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.event_type == event_type)
        )
        result = await db.execute(query)
        return result.scalar()
    
    async def count_by_date_range(
        self, 
        db: AsyncSession, 
        *, 
        start_date: datetime, 
        end_date: datetime, 
        camera_id: Optional[int] = None,
        event_type: Optional[str] = None
    ) -> int:
        """Count events for a specific period"""
        if start_date.tzinfo:
            start_date = start_date.replace(tzinfo=None)
        if end_date.tzinfo:
            end_date = end_date.replace(tzinfo=None)
            
        query = select(func.count()).select_from(self.model)
        
        query = query.where(between(self.model.timestamp, start_date, end_date))
        
        if camera_id is not None:
            query = query.where(self.model.camera_id == camera_id)
        
        if event_type is not None:
            query = query.where(self.model.event_type == event_type)
        
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def create_with_objects(
        self, 
        db: AsyncSession, 
        *, 
        event_in: EventCreate
    ) -> Event:
        """Create an event with objects"""
        from datetime import datetime
        
        event_data = event_in.dict(exclude={"objects"})
        
        for field, value in event_data.items():
            if isinstance(value, datetime) and value.tzinfo:
                event_data[field] = value.replace(tzinfo=None)
                
        db_event = self.model(**event_data)
        
        if event_in.objects:
            objects = []
            for obj_in in event_in.objects:
                obj_data = obj_in.dict(exclude={"event_id"})
                for field, value in obj_data.items():
                    if isinstance(value, datetime) and value.tzinfo:
                        obj_data[field] = value.replace(tzinfo=None)
                objects.append(Object(**obj_data))
            db_event.objects = objects
        
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        
        return db_event
    
    async def update_confirmed_status(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        is_confirmed: bool
    ) -> Optional[Event]:
        """Update the confirmation status of an event"""
        event = await self.get(db, id=id)
        if not event:
            return None
        
        event.is_confirmed = is_confirmed
        event.updated_at = datetime.utcnow()
        
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event
    
    async def update_false_positive_status(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        is_false_positive: bool
    ) -> Optional[Event]:
        """Update the false positive status of an event"""
        event = await self.get(db, id=id)
        if not event:
            return None
        
        event.is_false_positive = is_false_positive
        event.updated_at = datetime.utcnow()
        
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event
    
    async def get_stats(self, db: AsyncSession) -> EventStats:
        """Get statistics for events"""
        total_query = select(func.count()).select_from(self.model)
        total_result = await db.execute(total_query)
        total_events = total_result.scalar() or 0
        
        by_type_query = (
            select(self.model.event_type, func.count())
            .group_by(self.model.event_type)
        )
        by_type_result = await db.execute(by_type_query)
        by_type = {row[0]: row[1] for row in by_type_result.all()}
        
        by_camera_query = (
            select(self.model.camera_id, func.count())
            .group_by(self.model.camera_id)
        )
        by_camera_result = await db.execute(by_camera_query)
        by_camera = {row[0]: row[1] for row in by_camera_result.all()}
        
        confirmed_query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.is_confirmed == True)
        )
        confirmed_result = await db.execute(confirmed_query)
        confirmed_events = confirmed_result.scalar() or 0
        
        false_positives_query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.is_false_positive == True)
        )
        false_positives_result = await db.execute(false_positives_query)
        false_positives = false_positives_result.scalar() or 0
        
        return EventStats(
            total_events=total_events,
            by_type=by_type,
            by_camera=by_camera,
            confirmed_events=confirmed_events,
            false_positives=false_positives
        ) 