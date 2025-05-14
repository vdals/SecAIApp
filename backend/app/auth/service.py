from datetime import timedelta
from typing import Optional, List, Dict, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.auth.models import Permission, Role
from app.auth.repository import PermissionRepository, RoleRepository
from app.auth.schemas import (
    PermissionCreate, PermissionUpdate, Permission as PermissionSchema,
    RoleCreate, RoleUpdate, Role as RoleSchema, Token, TokenPayload
)
from app.common.utils import (
    create_access_token, create_refresh_token, verify_password,
    UnauthorizedException, ForbiddenException
)
from app.config import settings
from app.db.session import get_db
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, User as UserSchema


class AuthService:
    """Authentication and authorization service"""
    
    def __init__(
        self,
        user_repository: UserRepository = UserRepository(),
        role_repository: RoleRepository = RoleRepository()
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository
    
    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authentication user"""
        user = await self.user_repository.get_by_email(db, email=email)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return await self.user_repository.get_with_role(db, id=user.id)
    
    async def create_token(self, user_id: int) -> Token:
        """Create tokens for user"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            data={"sub": str(user_id)}, expires_delta=access_token_expires
        )
        
        refresh_token = create_refresh_token(
            data={"sub": str(user_id)}, expires_delta=refresh_token_expires
        )
        
        return Token(access_token=access_token, refresh_token=refresh_token)
    
    async def refresh_token(self, db: AsyncSession, refresh_token: str) -> Token:
        """Refresh token"""
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            token_data = TokenPayload(**payload)
            
            if token_data.sub is None:
                raise UnauthorizedException("Invalid token")
            
            user = await self.user_repository.get_with_role(db, id=token_data.sub)
            
            if not user:
                raise UnauthorizedException("User not found")
            
            return await self.create_token(user.id)
            
        except JWTError:
            raise UnauthorizedException("Invalid token")
    
    async def register_user(self, db: AsyncSession, user_in: UserCreate) -> UserSchema:
        """Registration new user"""
        existing_user = await self.user_repository.get_by_email(db, email=user_in.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        user = await self.user_repository.create(db, obj_in=user_in)
        user_dict = {}
        for key in user.__dict__:
            if not key.startswith('_'):
                user_dict[key] = getattr(user, key)
        return UserSchema.model_validate(user_dict)
    
    async def check_permission(
        self, 
        db: AsyncSession, 
        user_id: int, 
        permission_name: str
    ) -> bool:
        """Check user permission"""
        user = await self.user_repository.get_with_role(db, id=user_id)
        
        if not user or not user.role:
            return False
        
        if user.role.name == "admin":
            return True
            
        db_permission_mapping = {
            "manage_locations": "locations.manage",
            "manage_events": "events.manage",
            "manage_cameras": "cameras.manage",
            "manage_videos": "videos.manage",
            "locations.manage": "manage_locations",
            "events.manage": "manage_events",
            "cameras.manage": "manage_cameras",
            "videos.manage": "manage_videos"
        }
        
        original_perm = permission_name
        mapped_perm = db_permission_mapping.get(permission_name, permission_name)
        
        user_permissions = [perm.name for perm in user.role.permissions]
        
        return original_perm in user_permissions or mapped_perm in user_permissions
    
    async def require_permission(
        self, 
        db: AsyncSession, 
        user_id: int, 
        permission_name: str
    ) -> None:
        """Require user permission"""
        has_permission = await self.check_permission(db, user_id, permission_name)
        
        if not has_permission:
            raise ForbiddenException(f"User doesn't have permission: {permission_name}")


class PermissionService:
    """Service for working with permissions"""
    
    def __init__(self, repository: PermissionRepository = PermissionRepository()):
        self.repository = repository
    
    async def get_all(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[PermissionSchema]:
        """Get all permissions"""
        permissions = await self.repository.get_all(db, skip=skip, limit=limit)
        # Преобразуем SQLAlchemy модели в словари
        perm_dicts = [self._model_to_dict(p) for p in permissions]
        return [PermissionSchema.model_validate(p) for p in perm_dicts]
    
    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[PermissionSchema]:
        """Get permission by ID"""
        permission = await self.repository.get(db, id=id)
        if not permission:
            return None
        perm_dict = self._model_to_dict(permission)
        return PermissionSchema.model_validate(perm_dict)
    
    async def create(
        self, 
        db: AsyncSession, 
        permission_in: PermissionCreate
    ) -> PermissionSchema:
        """Create permission"""
        permission = await self.repository.create(db, obj_in=permission_in)
        perm_dict = self._model_to_dict(permission)
        return PermissionSchema.model_validate(perm_dict)
    
    async def update(
        self, 
        db: AsyncSession, 
        id: int, 
        permission_in: PermissionUpdate
    ) -> Optional[PermissionSchema]:
        """Update permission"""
        permission = await self.repository.get(db, id=id)
        if not permission:
            return None
        
        updated_permission = await self.repository.update(
            db, db_obj=permission, obj_in=permission_in
        )
        perm_dict = self._model_to_dict(updated_permission)
        return PermissionSchema.model_validate(perm_dict)
    
    async def delete(self, db: AsyncSession, id: int) -> bool:
        """Delete permission"""
        return await self.repository.delete(db, id=id)
    
    def _model_to_dict(self, model: Permission) -> Dict[str, Any]:
        """Convert SQLAlchemy model to dictionary"""
        result = {}
        for key in model.__dict__:
            if not key.startswith('_'):
                result[key] = getattr(model, key)
        return result


class RoleService:
    """Service for working with roles"""
    
    def __init__(self, repository: RoleRepository = RoleRepository()):
        self.repository = repository
    
    async def get_all(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[RoleSchema]:
        """Get all roles"""
        roles = await self.repository.get_all(db, skip=skip, limit=limit)

        role_dicts = [self._model_to_dict(r) for r in roles]
        return [RoleSchema.model_validate(r) for r in role_dicts]
    
    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[RoleSchema]:
        """Get role by ID"""
        role = await self.repository.get_with_permissions(db, role_id=id)
        if not role:
            return None
        role_dict = self._model_to_dict(role)
        return RoleSchema.model_validate(role_dict)
    
    async def create(self, db: AsyncSession, role_in: RoleCreate) -> RoleSchema:
        """Create role"""
        role = await self.repository.create(db, obj_in=role_in)
        created_role = await self.repository.get_with_permissions(db, role_id=role.id)
        role_dict = self._model_to_dict(created_role)
        return RoleSchema.model_validate(role_dict)
    
    async def update(
        self, 
        db: AsyncSession, 
        id: int, 
        role_in: RoleUpdate
    ) -> Optional[RoleSchema]:
        """Update role"""
        role = await self.repository.get(db, id=id)
        if not role:
            return None
        
        updated_role = await self.repository.update(db, db_obj=role, obj_in=role_in)
        role_with_permissions = await self.repository.get_with_permissions(
            db, role_id=updated_role.id
        )
        role_dict = self._model_to_dict(role_with_permissions)
        return RoleSchema.model_validate(role_dict)
    
    async def delete(self, db: AsyncSession, id: int) -> bool:
        """Delete role"""
        return await self.repository.delete(db, id=id)
    
    def _model_to_dict(self, model: Role) -> Dict[str, Any]:
        """Convert SQLAlchemy model to dictionary with full conversion of nested objects"""
        result = {}
        for key in model.__dict__:
            if not key.startswith('_'):
                value = getattr(model, key)
                if key == 'permissions' and value:
                    permissions = []
                    for perm in value:
                        permissions.append({
                            'id': perm.id,
                            'name': perm.name,
                            'description': perm.description,
                            'created_at': perm.created_at,
                            'updated_at': perm.updated_at
                        })
                    result[key] = permissions
                else:
                    result[key] = value
        return result 