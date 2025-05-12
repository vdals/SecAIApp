from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from app.common.schemas import BaseSchema, BaseSchemaWithId
# Импорты на уровне модуля
from app.cameras.schemas import Camera


class ObjectBase(BaseSchema):
    """Base object schema"""
    object_type: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    attributes: Optional[Dict[str, Any]] = None


class ObjectCreate(ObjectBase):
    """Schema for creating object"""
    event_id: int


class ObjectUpdate(BaseSchema):
    """Schema for updating object"""
    object_type: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    x_min: Optional[int] = None
    y_min: Optional[int] = None
    x_max: Optional[int] = None
    y_max: Optional[int] = None
    attributes: Optional[Dict[str, Any]] = None


class Object(ObjectBase, BaseSchemaWithId):
    """Full object schema"""
    event_id: int


class EventBase(BaseSchema):
    """Base event schema"""
    event_type: str
    timestamp: datetime
    description: Optional[str] = None
    is_confirmed: bool = False
    is_false_positive: bool = False
    frame_number: Optional[int] = None
    frame_timestamp: Optional[datetime] = None
    frame_path: Optional[str] = None
    camera_id: int
    video_id: Optional[int] = None


class EventCreate(EventBase):
    """Schema for creating event"""
    objects: Optional[List[ObjectCreate]] = []


class EventUpdate(BaseSchema):
    """Schema for updating event"""
    event_type: Optional[str] = None
    timestamp: Optional[datetime] = None
    description: Optional[str] = None
    is_confirmed: Optional[bool] = None
    is_false_positive: Optional[bool] = None
    frame_number: Optional[int] = None
    frame_timestamp: Optional[datetime] = None
    frame_path: Optional[str] = None
    camera_id: Optional[int] = None
    video_id: Optional[int] = None


class Event(EventBase, BaseSchemaWithId):
    """Full event schema"""
    pass


class EventWithObjects(Event):
    """Event schema with objects"""
    objects: List[Object] = []


class EventWithCamera(Event):
    """Event schema with camera"""
    __module__ = 'app.events.schemas'
    camera: Camera


class EventWithVideo(Event):
    """Event schema with video"""
    video: Optional[Any] = None


class EventFull(EventWithObjects, EventWithCamera, EventWithVideo):
    """Full event schema with all relations"""
    pass


class AIDetectionResult(BaseSchema):
    """AI detection result"""
    event_type: str
    confidence: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    frame_number: Optional[int] = None
    frame_timestamp: Optional[datetime] = None
    frame_path: Optional[str] = None
    camera_id: int
    video_id: Optional[int] = None
    objects: List[ObjectBase] = []
    

class EventStats(BaseSchema):
    """Event statistics"""
    total_events: int
    by_type: Dict[str, int]
    by_camera: Dict[int, int]
    confirmed_events: int
    false_positives: int