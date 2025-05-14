from __future__ import annotations
from typing import List, Optional, Any

from pydantic import BaseModel, Field, ConfigDict

from app.common.schemas import BaseSchema, BaseSchemaWithId


class LocationBase(BaseSchema):
    """Base location schema"""
    name: str
    address: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class LocationCreate(LocationBase):
    """Schema for creating location"""
    pass


class LocationUpdate(BaseSchema):
    """Schema for updating location"""
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Location(LocationBase, BaseSchemaWithId):
    """Full location schema"""
    pass


# Import here to avoid circular imports
from app.users.schemas import UserBase, BaseSchemaWithId as UserBaseSchemaWithId

class UserInLocation(UserBase, UserBaseSchemaWithId):
    """Simplified user schema for location display"""
    pass


class LocationWithUsers(Location):
    """Location schema with users"""
    users: List[UserInLocation] = []


class LocationWithCameras(Location):
    """Location schema with cameras"""
    cameras: List[Any] = []


class LocationFull(LocationWithUsers, LocationWithCameras):
    """Full location schema with users and cameras"""
    pass 