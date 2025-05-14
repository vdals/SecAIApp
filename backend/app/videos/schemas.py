from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Any

from pydantic import BaseModel, Field, validator

from app.common.schemas import BaseSchema, BaseSchemaWithId
# Импорты на уровне модуля
from app.cameras.schemas import Camera


class VideoBase(BaseSchema):
    """Базовая схема видео"""
    filename: str
    filepath: str
    file_size: int = Field(0, ge=0)
    duration: Optional[int] = Field(None, ge=0)
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    fps: Optional[int] = None
    codec: Optional[str] = None
    format: Optional[str] = None
    recording_start: datetime
    recording_end: Optional[datetime] = None
    is_processed: bool = False
    is_analyzed: bool = False
    processing_status: str = "pending"
    camera_id: int


class VideoCreate(VideoBase):
    """Схема для создания видео"""
    pass


class VideoUpdate(BaseSchema):
    """Схема для обновления видео"""
    filename: Optional[str] = None
    filepath: Optional[str] = None
    file_size: Optional[int] = Field(None, ge=0)
    duration: Optional[int] = Field(None, ge=0)
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    fps: Optional[int] = None
    codec: Optional[str] = None
    format: Optional[str] = None
    recording_start: Optional[datetime] = None
    recording_end: Optional[datetime] = None
    is_processed: Optional[bool] = None
    is_analyzed: Optional[bool] = None
    processing_status: Optional[str] = None
    camera_id: Optional[int] = None


class Video(VideoBase, BaseSchemaWithId):
    """Полная схема видео"""
    
    @validator('recording_end')
    def validate_recording_end(cls, v, values):
        if v is not None and 'recording_start' in values and v < values['recording_start']:
            raise ValueError('recording_end must be after recording_start')
        return v


class VideoWithCamera(Video):
    """Схема видео с информацией о камере"""
    __module__ = 'app.videos.schemas'
    camera: Camera


class VideoWithEvents(Video):
    """Схема видео с информацией о событиях"""
    events: List[Any] = []


class VideoFull(VideoWithCamera, VideoWithEvents):
    """Полная схема видео с камерой и событиями"""
    pass


class VideoProcessStatus(BaseSchema):
    """Схема статуса обработки видео"""
    video_id: int
    status: str
    message: Optional[str] = None
    progress: Optional[float] = Field(None, ge=0, le=100)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class VideoUpload(BaseSchema):
    """Схема для загрузки видео"""
    camera_id: int
    recording_start: Optional[datetime] = None
    recording_end: Optional[datetime] = None


class VideoSegmentInfo(BaseSchema):
    """Информация о видеосегменте"""
    video_id: int
    segment_number: int
    segment_path: str
    duration: float
    format: str


# Регистрируем forward references
# VideoWithEvents.model_rebuild()
# VideoFull.model_rebuild() 