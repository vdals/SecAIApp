from typing import List, Optional

from pydantic import EmailStr, Field

from app.common.schemas import BaseSchema, BaseSchemaWithId


# Permissions schemas
class PermissionBase(BaseSchema):
    name: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    name: Optional[str] = None


class Permission(PermissionBase, BaseSchemaWithId):
    pass


# Roles schemas
class RoleBase(BaseSchema):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = []


class RoleUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class Role(RoleBase, BaseSchemaWithId):
    permissions: List[Permission] = []


class RoleWithPermissions(Role):
    """Role schema with full list of permissions"""
    permissions: List[Permission]


# Authorization schemas
class Token(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseSchema):
    sub: Optional[int] = None
    exp: Optional[int] = None


class RefreshToken(BaseSchema):
    refresh_token: str


# Login schema
class Login(BaseSchema):
    email: EmailStr
    password: str


# Registration schema
class UserCreate(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str
    role_id: Optional[int] = None 