from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import PaginatedResult
from app.common.utils import get_password_hash, verify_password
from app.users.models import User as UserModel
from app.users.repository import UserRepository
from app.users.schemas import (
    User as UserSchema,
    UserCreate,
    UserUpdate,
    UserWithLocations,
    UserWithRole,
    UserChangePassword
)


class UserService:
    """Service for working with users"""
    
    def __init__(self, repository: UserRepository = UserRepository()):
        self.repository = repository
    
    async def get_all(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filter_by: Optional[dict] = None
    ) -> PaginatedResult[UserSchema]:
        """Get all users with pagination"""
        users = await self.repository.get_all(db, skip=skip, limit=limit, filters=filter_by)
        total = await self.repository.count(db, filters=filter_by)
        
        user_dicts = [self._model_to_dict(user) for user in users]
        
        return PaginatedResult.create(
            items=[UserSchema.model_validate(u) for u in user_dicts], 
            total=total, 
            skip=skip, 
            limit=limit
        )
    
    async def get_by_id(self, db: AsyncSession, *, id: int) -> Optional[UserWithRole]:
        """Get user by ID with full role and permissions information"""
        user = await self.repository.get_with_role(db, id=id)
        if not user:
            return None
        user_dict = self._model_to_dict(user)
        return UserWithRole.model_validate(user_dict)
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[UserWithRole]:
        """Get user by email with full role and permissions information"""
        user = await self.repository.get_by_email(db, email=email)
        if not user:
            return None
        
        return await self.get_by_id(db, id=user.id)
    
    async def get_with_locations(self, db: AsyncSession, *, id: int) -> Optional[UserWithLocations]:
        """Get user with locations"""
        user = await self.repository.get_with_locations(db, id=id)
        if not user:
            return None
        user_dict = self._model_to_dict(user)
        return UserWithLocations.model_validate(user_dict)
    
    async def create(self, db: AsyncSession, *, user_in: UserCreate) -> UserSchema:
        """Create user"""
        existing_user = await self.repository.get_by_email(db, email=user_in.email)
        if existing_user:
            raise ValueError("User with such email already exists")
        
        user = await self.repository.create(db, obj_in=user_in)
        user_dict = self._model_to_dict(user)
        return UserSchema.model_validate(user_dict)
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        user_in: UserUpdate
    ) -> Optional[UserSchema]:
        """Update user"""
        user = await self.repository.get(db, id=id)
        if not user:
            return None
        
        if user_in.email and user_in.email != user.email:
            existing_user = await self.repository.get_by_email(db, email=user_in.email)
            if existing_user:
                raise ValueError("User with such email already exists")
        
        updated_user = await self.repository.update(db, db_obj=user, obj_in=user_in)
        user_dict = self._model_to_dict(updated_user)
        return UserSchema.model_validate(user_dict)
    
    async def delete(self, db: AsyncSession, *, id: int) -> bool:
        """Delete user"""
        return await self.repository.delete(db, id=id)
    
    async def change_password(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        current_password: str, 
        new_password: str
    ) -> Optional[UserSchema]:
        """Change user password"""
        user = await self.repository.get(db, id=id)
        if not user:
            return None
        
        if not verify_password(current_password, user.hashed_password):
            raise ValueError("Invalid current password")
        
        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        user_dict = self._model_to_dict(user)
        return UserSchema.model_validate(user_dict)
    
    async def add_to_location(
        self, 
        db: AsyncSession, 
        *, 
        user_id: int, 
        location_id: int
    ) -> Optional[UserWithLocations]:
        """Add user to location"""
        user = await self.repository.add_to_location(db, user_id=user_id, location_id=location_id)
        if not user:
            return None
        user_dict = self._model_to_dict(user)
        return UserWithLocations.model_validate(user_dict)
    
    async def remove_from_location(
        self, 
        db: AsyncSession, 
        *, 
        user_id: int, 
        location_id: int
    ) -> Optional[UserWithLocations]:
        """Remove user from location"""
        user = await self.repository.remove_from_location(db, user_id=user_id, location_id=location_id)
        if not user:
            return None
        user_dict = self._model_to_dict(user)
        return UserWithLocations.model_validate(user_dict)

    async def get_with_role(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[UserWithRole]:
        """Get user with role and permissions"""
        user = await self.repository.get_with_role(db, id=id)
        if not user:
            return None
        user_dict = self._model_to_dict(user)
        return UserWithRole.model_validate(user_dict)
    
    def _model_to_dict(self, model: UserModel) -> Dict[str, Any]:
        """Convert SQLAlchemy model to dictionary with full conversion of nested objects"""
        result = {}
        for key in model.__dict__:
            if not key.startswith('_'):
                value = getattr(model, key)
                if key == 'role' and value is not None:
                    role_dict = {
                        'id': value.id,
                        'name': value.name,
                        'description': value.description,
                        'created_at': value.created_at,
                        'updated_at': value.updated_at,
                        'permissions': []
                    }
                    
                    if hasattr(value, 'permissions') and value.permissions:
                        for perm in value.permissions:
                            role_dict['permissions'].append({
                                'id': perm.id,
                                'name': perm.name,
                                'description': perm.description,
                                'created_at': perm.created_at,
                                'updated_at': perm.updated_at
                            })
                    result[key] = role_dict
                elif key == 'locations' and value:
                    locations = []
                    for loc in value:
                        locations.append({
                            'id': loc.id,
                            'name': loc.name,
                            'address': loc.address,
                            'description': loc.description,
                            'latitude': loc.latitude,
                            'longitude': loc.longitude,
                            'created_at': loc.created_at,
                            'updated_at': loc.updated_at
                        })
                    result[key] = locations
                else:
                    result[key] = value
        return result 