from __future__ import annotations
from typing import List, Optional, Any

from pydantic import BaseModel, Field, validator

from app.common.schemas import BaseSchema, BaseSchemaWithId


class CameraBase(BaseSchema):
    """Base camera schema"""
    name: str
    ip_address: Optional[str] = None
    rtsp_url: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    location_id: int
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    fps: Optional[int] = None
    rotation: Optional[int] = Field(None, ge=0, lt=360)
    timezone: Optional[str] = None


class CameraCreate(CameraBase):
    """Schema for creating a camera"""
    owner_id: Optional[int] = None  # If None, the owner will be the current user


class CameraUpdate(BaseSchema):
    """Schema for updating a camera"""
    name: Optional[str] = None
    ip_address: Optional[str] = None
    rtsp_url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    location_id: Optional[int] = None
    owner_id: Optional[int] = None
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    fps: Optional[int] = None
    rotation: Optional[int] = Field(None, ge=0, lt=360)
    timezone: Optional[str] = None


class Camera(CameraBase, BaseSchemaWithId):
    """Full camera schema"""
    owner_id: int

    @validator('rotation')
    def validate_rotation(cls, v):
        if v is not None and (v < 0 or v >= 360):
            raise ValueError('Rotation must be between 0 and 359 degrees')
        return v


class CameraWithLocation(Camera):
    """Camera schema with location information"""
    location: Any


class CameraWithOwner(Camera):
    """Camera schema with owner information"""
    owner: Any


class CameraFull(CameraWithLocation, CameraWithOwner):
    """Full camera schema with location and owner"""
    pass


class CameraStats(BaseSchema):
    """Camera statistics"""
    total_videos: int = 0
    total_events: int = 0
    disk_usage_mb: float = 0.0
