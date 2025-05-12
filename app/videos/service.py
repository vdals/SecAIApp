import os
from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.cameras.repository import CameraRepository
from app.common.schemas import PaginatedResult
from app.common.utils import NotFoundException, ForbiddenException
from app.videos.models import Video
from app.videos.repository import VideoRepository
from app.videos.schemas import (
    Video as VideoSchema,
    VideoCreate, 
    VideoUpdate,
    VideoWithCamera,
    VideoWithEvents,
    VideoFull,
    VideoProcessStatus,
    VideoUpload
)


class VideoService:
    """Service for working with videos"""
    
    def __init__(
        self, 
        repository: VideoRepository = VideoRepository(),
        camera_repository: CameraRepository = CameraRepository()
    ):
        self.repository = repository
        self.camera_repository = camera_repository
    
    async def get_all(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[VideoSchema]:
        """Get all videos with pagination"""
        videos = await self.repository.get_all(db, skip=skip, limit=limit)
        total = await self.repository.count(db)
        
        return PaginatedResult.create(
            items=[VideoSchema.model_validate(v) for v in videos],
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
    ) -> PaginatedResult[VideoSchema]:
        """Get all videos for a specific camera with pagination"""
        camera = await self.camera_repository.get(db, id=camera_id)
        if not camera:
            raise NotFoundException(f"Camera with ID {camera_id} not found")
        
        videos = await self.repository.get_all_by_camera(
            db, camera_id=camera_id, skip=skip, limit=limit
        )
        total = await self.repository.count_by_camera(db, camera_id=camera_id)
        
        return PaginatedResult.create(
            items=[VideoSchema.model_validate(v) for v in videos],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_by_date_range(
        self, 
        db: AsyncSession, 
        *, 
        start_date: datetime, 
        end_date: datetime, 
        camera_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[VideoSchema]:
        """Get videos for a specific date range with pagination"""
        if camera_id is not None:
            camera = await self.camera_repository.get(db, id=camera_id)
            if not camera:
                raise NotFoundException(f"Camera with ID {camera_id} not found")
        
        videos = await self.repository.get_by_date_range(
            db, 
            start_date=start_date, 
            end_date=end_date, 
            camera_id=camera_id,
            skip=skip, 
            limit=limit
        )
        total = await self.repository.count_by_date_range(
            db, 
            start_date=start_date, 
            end_date=end_date, 
            camera_id=camera_id
        )
        
        return PaginatedResult.create(
            items=[VideoSchema.model_validate(v) for v in videos],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_by_id(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[VideoSchema]:
        """Get video by ID"""
        video = await self.repository.get(db, id=id)
        if not video:
            return None
        return VideoSchema.model_validate(video)
    
    async def get_with_camera(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[VideoWithCamera]:
        """Get video with camera information by ID"""
        video = await self.repository.get_with_camera(db, id=id)
        if not video:
            return None
        return VideoWithCamera.model_validate(video)
    
    async def get_with_events(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[VideoWithEvents]:
        """Get video with events information by ID"""
        video = await self.repository.get_with_events(db, id=id)
        if not video:
            return None
        return VideoWithEvents.model_validate(video)
    
    async def get_full(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[VideoFull]:
        """Get video with camera and events information by ID"""
        video = await self.repository.get_full(db, id=id)
        if not video:
            return None
        return VideoFull.model_validate(video)
    
    async def create(
        self, 
        db: AsyncSession, 
        *, 
        video_in: VideoCreate
    ) -> VideoFull:
        """Create video"""
        camera = await self.camera_repository.get(db, id=video_in.camera_id)
        if not camera:
            raise NotFoundException(f"Camera with ID {video_in.camera_id} not found")
        
        video = await self.repository.create(db, obj_in=video_in)
        
        video_full = await self.repository.get_full(db, id=video.id)
        return VideoFull.model_validate(video_full)
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        video_in: VideoUpdate
    ) -> Optional[VideoFull]:
        """Update video"""
        video = await self.repository.get(db, id=id)
        if not video:
            return None
        
        if video_in.camera_id is not None:
            camera = await self.camera_repository.get(db, id=video_in.camera_id)
            if not camera:
                raise NotFoundException(f"Camera with ID {video_in.camera_id} not found")
        
        updated_video = await self.repository.update(db, db_obj=video, obj_in=video_in)
        
        video_full = await self.repository.get_full(db, id=updated_video.id)
        return VideoFull.model_validate(video_full)
    
    async def delete(
        self, 
        db: AsyncSession, 
        *, 
        id: int,
        delete_file: bool = False
    ) -> bool:
        """Delete video"""
        video = await self.repository.get(db, id=id)
        if not video:
            return False
        
        if delete_file and video.filepath:
            try:
                if os.path.exists(video.filepath):
                    os.remove(video.filepath)
            except Exception as e:
                print(f"Error deleting file {video.filepath}: {e}")
        
        return await self.repository.delete(db, id=id)
    
    async def update_processing_status(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        status: str
    ) -> Optional[VideoSchema]:
        """Update video processing status"""
        video = await self.repository.update_processing_status(db, id=id, status=status)
        if not video:
            return None
        return VideoSchema.model_validate(video)
    
    async def update_analysis_status(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        is_analyzed: bool
    ) -> Optional[VideoSchema]:
        """Update video analysis status"""
        video = await self.repository.update_analysis_status(db, id=id, is_analyzed=is_analyzed)
        if not video:
            return None
        return VideoSchema.model_validate(video)
    
    async def get_latest_by_camera(
        self, 
        db: AsyncSession, 
        *, 
        camera_id: int, 
        limit: int = 5
    ) -> List[VideoSchema]:
        """Get latest videos for a specific camera"""
        camera = await self.camera_repository.get(db, id=camera_id)
        if not camera:
            raise NotFoundException(f"Camera with ID {camera_id} not found")
        
        videos = await self.repository.get_latest_by_camera(
            db, camera_id=camera_id, limit=limit
        )
        return [VideoSchema.model_validate(v) for v in videos]
    
    async def handle_upload(
        self, 
        db: AsyncSession, 
        *, 
        file_path: str,
        file_size: int,
        upload_info: VideoUpload
    ) -> VideoSchema:
        """Handle uploaded file"""
        camera = await self.camera_repository.get(db, id=upload_info.camera_id)
        if not camera:
            raise NotFoundException(f"Camera with ID {upload_info.camera_id} not found")
        
        filename = os.path.basename(file_path)
        
        recording_start = upload_info.recording_start or datetime.utcnow()
        if recording_start.tzinfo:
            recording_start = recording_start.replace(tzinfo=None)
            
        recording_end = upload_info.recording_end
        if recording_end and recording_end.tzinfo:
            recording_end = recording_end.replace(tzinfo=None)
        
        video_data = VideoCreate(
            filename=filename,
            filepath=file_path,
            file_size=file_size,
            camera_id=upload_info.camera_id,
            recording_start=recording_start,
            recording_end=recording_end,
            processing_status="uploaded"
        )
        
        video = await self.repository.create(db, obj_in=video_data)
        
        video_dict = {}
        for key in video.__dict__:
            if not key.startswith('_'):
                video_dict[key] = getattr(video, key)
                
        return VideoSchema.model_validate(video_dict) 