from __future__ import annotations
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.auth.schemas import Role, RoleWithPermissions
from app.common.schemas import BaseSchema, BaseSchemaWithId


class UserBase(BaseSchema):
    """Base user schema"""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    role_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    """Schema for creating user"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    """Schema for updating user"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    role_id: Optional[int] = None


class User(UserBase, BaseSchemaWithId):
    """Full user schema"""
    role: Optional[Role] = None


# Import here to avoid circular imports
from app.locations.schemas import Location as LocationSchema

class UserWithLocations(User):
    """User schema with locations"""
    locations: List[LocationSchema] = []


class UserFull(User):
    """Full user schema with locations"""
    locations: List[LocationSchema] = []


class UserChangePassword(BaseSchema):
    """Schema for changing password"""
    current_password: str
    new_password: str = Field(..., min_length=8)


class UserWithRole(UserBase, BaseSchemaWithId):
    """User schema with full role and permissions information"""
    role: Optional[RoleWithPermissions] = None 