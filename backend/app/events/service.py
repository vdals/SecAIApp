from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.cameras.repository import CameraRepository
from app.common.schemas import PaginatedResult
from app.common.utils import NotFoundException
from app.events.models import Event, Object
from app.events.repository import EventRepository, ObjectRepository
from app.events.schemas import (
    Event as EventSchema,
    EventCreate, 
    EventUpdate,
    EventWithObjects,
    EventWithCamera,
    EventWithVideo,
    EventFull,
    AIDetectionResult,
    EventStats,
    Object as ObjectSchema,
    ObjectCreate,
    ObjectUpdate
)
from app.videos.repository import VideoRepository


class ObjectService:
    """Service for working with objects"""
    
    def __init__(self, repository: ObjectRepository = ObjectRepository()):
        self.repository = repository
    
    async def get_all_by_event(
        self, 
        db: AsyncSession, 
        *, 
        event_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[ObjectSchema]:
        """Get all objects for a specific event with pagination"""
        objects = await self.repository.get_all_by_event(
            db, event_id=event_id, skip=skip, limit=limit
        )
        total = await self.repository.count_by_event(db, event_id=event_id)
        
        return PaginatedResult.create(
            items=[ObjectSchema.model_validate(o) for o in objects],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_by_id(self, db: AsyncSession, *, id: int) -> Optional[ObjectSchema]:
        """Get object by ID"""
        obj = await self.repository.get(db, id=id)
        if not obj:
            return None
        return ObjectSchema.model_validate(obj)
    
    async def create(self, db: AsyncSession, *, obj_in: ObjectCreate) -> ObjectSchema:
        """Create object"""
        obj = await self.repository.create(db, obj_in=obj_in)
        return ObjectSchema.model_validate(obj)
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        obj_in: ObjectUpdate
    ) -> Optional[ObjectSchema]:
        """Update object"""
        obj = await self.repository.get(db, id=id)
        if not obj:
            return None
        
        updated_obj = await self.repository.update(db, db_obj=obj, obj_in=obj_in)
        return ObjectSchema.model_validate(updated_obj)
    
    async def delete(self, db: AsyncSession, *, id: int) -> bool:
        """Delete object"""
        return await self.repository.delete(db, id=id)


class EventService:
    """Service for working with events"""
    
    def __init__(
        self, 
        repository: EventRepository = EventRepository(),
        object_repository: ObjectRepository = ObjectRepository(),
        camera_repository: CameraRepository = CameraRepository(),
        video_repository: VideoRepository = VideoRepository()
    ):
        self.repository = repository
        self.object_repository = object_repository
        self.camera_repository = camera_repository
        self.video_repository = video_repository
    
    async def get_all(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[EventSchema]:
        """Get all events with pagination"""
        events = await self.repository.get_all(db, skip=skip, limit=limit)
        total = await self.repository.count(db)
        
        return PaginatedResult.create(
            items=[EventSchema.model_validate(e) for e in events],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_all_by_camera(
        self, 
        db: AsyncSession, 
        *, 
        camera_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[EventSchema]:
        """Get all events for a specific camera with pagination"""
        camera = await self.camera_repository.get(db, id=camera_id)
        if not camera:
            raise NotFoundException(f"Camera with ID {camera_id} not found")
        
        events = await self.repository.get_all_by_camera(
            db, camera_id=camera_id, skip=skip, limit=limit
        )
        total = await self.repository.count_by_camera(db, camera_id=camera_id)
        
        return PaginatedResult.create(
            items=[EventSchema.model_validate(e) for e in events],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_all_by_video(
        self, 
        db: AsyncSession, 
        *, 
        video_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[EventSchema]:
        """Get all events for a specific video with pagination"""
        video = await self.video_repository.get(db, id=video_id)
        if not video:
            raise NotFoundException(f"Video with ID {video_id} not found")
        
        events = await self.repository.get_all_by_video(
            db, video_id=video_id, skip=skip, limit=limit
        )
        total = await self.repository.count_by_video(db, video_id=video_id)
        
        return PaginatedResult.create(
            items=[EventSchema.model_validate(e) for e in events],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_all_by_type(
        self, 
        db: AsyncSession, 
        *, 
        event_type: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[EventSchema]:
        """Get all events of a specific type with pagination"""
        events = await self.repository.get_all_by_type(
            db, event_type=event_type, skip=skip, limit=limit
        )
        total = await self.repository.count_by_type(db, event_type=event_type)
        
        return PaginatedResult.create(
            items=[EventSchema.model_validate(e) for e in events],
            total=total,
            skip=skip,
            limit=limit
        )
    
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
    ) -> PaginatedResult[EventSchema]:
        """Get all events for a specific period with pagination"""
        if camera_id is not None:
            camera = await self.camera_repository.get(db, id=camera_id)
            if not camera:
                raise NotFoundException(f"Camera with ID {camera_id} not found")
        
        events = await self.repository.get_all_by_date_range(
            db, 
            start_date=start_date, 
            end_date=end_date, 
            camera_id=camera_id,
            event_type=event_type,
            skip=skip, 
            limit=limit
        )
        total = await self.repository.count_by_date_range(
            db, 
            start_date=start_date, 
            end_date=end_date, 
            camera_id=camera_id,
            event_type=event_type
        )
        
        return PaginatedResult.create(
            items=[EventSchema.model_validate(e) for e in events],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_by_id(self, db: AsyncSession, *, id: int) -> Optional[EventSchema]:
        """Get event by ID"""
        event = await self.repository.get(db, id=id)
        if not event:
            return None
        return EventSchema.model_validate(event)
    
    async def get_with_objects(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[EventWithObjects]:
        """Get event with objects by ID"""
        event = await self.repository.get_with_objects(db, id=id)
        if not event:
            return None
        return EventWithObjects.model_validate(event)
    
    async def get_with_camera(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[EventWithCamera]:
        """Get event with camera by ID"""
        event = await self.repository.get_with_camera(db, id=id)
        if not event:
            return None
        return EventWithCamera.model_validate(event)
    
    async def get_with_video(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[EventWithVideo]:
        """Get event with video by ID"""
        event = await self.repository.get_with_video(db, id=id)
        if not event:
            return None
        return EventWithVideo.model_validate(event)
    
    async def get_full(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[EventFull]:
        """Get event with all relations by ID"""
        event = await self.repository.get_full(db, id=id)
        if not event:
            return None
        return EventFull.model_validate(event)
    
    async def create(
        self, 
        db: AsyncSession, 
        *, 
        event_in: EventCreate
    ) -> EventWithObjects:
        """Create event"""
        camera = await self.camera_repository.get(db, id=event_in.camera_id)
        if not camera:
            raise NotFoundException(f"Camera with ID {event_in.camera_id} not found")
        
        if event_in.video_id is not None:
            video = await self.video_repository.get(db, id=event_in.video_id)
            if not video:
                raise NotFoundException(f"Video with ID {event_in.video_id} not found")
        
        event = await self.repository.create_with_objects(db, event_in=event_in)
        
        event_with_objects = await self.repository.get_with_objects(db, id=event.id)
        return EventWithObjects.model_validate(event_with_objects)
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        event_in: EventUpdate
    ) -> Optional[EventSchema]:
        """Update event"""
        event = await self.repository.get(db, id=id)
        if not event:
            return None
        
        if event_in.camera_id is not None:
            camera = await self.camera_repository.get(db, id=event_in.camera_id)
            if not camera:
                raise NotFoundException(f"Camera with ID {event_in.camera_id} not found")
        
        if event_in.video_id is not None:
            video = await self.video_repository.get(db, id=event_in.video_id)
            if not video:
                raise NotFoundException(f"Video with ID {event_in.video_id} not found")
        
        updated_event = await self.repository.update(db, db_obj=event, obj_in=event_in)
        return EventSchema.model_validate(updated_event)
    
    async def delete(self, db: AsyncSession, *, id: int) -> bool:
        """Delete event"""
        return await self.repository.delete(db, id=id)
    
    async def update_confirmed_status(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        is_confirmed: bool
    ) -> Optional[EventSchema]:
        """Update confirmed status of event"""
        updated_event = await self.repository.update_confirmed_status(
            db, id=id, is_confirmed=is_confirmed
        )
        if not updated_event:
            return None
        return EventSchema.model_validate(updated_event)
    
    async def update_false_positive_status(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        is_false_positive: bool
    ) -> Optional[EventSchema]:
        """Update false positive status of event"""
        updated_event = await self.repository.update_false_positive_status(
            db, id=id, is_false_positive=is_false_positive
        )
        if not updated_event:
            return None
        return EventSchema.model_validate(updated_event)
    
    async def process_ai_detection(
        self, 
        db: AsyncSession, 
        *, 
        detection: AIDetectionResult
    ) -> EventWithObjects:
        """Process AI detection result"""
        camera = await self.camera_repository.get(db, id=detection.camera_id)
        if not camera:
            raise NotFoundException(f"Camera with ID {detection.camera_id} not found")
        
        if detection.video_id is not None:
            video = await self.video_repository.get(db, id=detection.video_id)
            if not video:
                raise NotFoundException(f"Video with ID {detection.video_id} not found")
        
        objects = []
        for obj in detection.objects:
            objects.append(ObjectCreate(
                event_id=0,  # will be replaced when event is created
                object_type=obj.object_type,
                confidence=obj.confidence,
                x_min=obj.x_min,
                y_min=obj.y_min,
                x_max=obj.x_max,
                y_max=obj.y_max,
                attributes=obj.attributes
            ))
        
        event_in = EventCreate(
            event_type=detection.event_type,
            timestamp=detection.timestamp,
            frame_number=detection.frame_number,
            frame_timestamp=detection.frame_timestamp,
            frame_path=detection.frame_path,
            camera_id=detection.camera_id,
            video_id=detection.video_id,
            objects=objects
        )
        
        return await self.create(db, event_in=event_in)
    
    async def get_stats(self, db: AsyncSession) -> EventStats:
        """Get statistics of events"""
        return await self.repository.get_stats(db) 