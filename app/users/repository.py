from typing import Any, Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.repository import BaseRepository
from app.common.utils import get_password_hash
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate
from app.auth.models import Role


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """User repository for working with users"""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Get user by email"""
        query = select(self.model).where(self.model.email == email)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_with_role(self, db: AsyncSession, *, id: int) -> Optional[User]:
        """Get user with role and permissions"""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.role).selectinload(Role.permissions)
            )
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_with_locations(self, db: AsyncSession, *, id: int) -> Optional[User]:
        """Get user with locations"""
        query = (
            select(self.model)
            .options(selectinload(self.model.locations))
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Create user with password hashing"""
        obj_in_data = obj_in.dict(exclude={"password"})
        obj_in_data["hashed_password"] = get_password_hash(obj_in.password)
        
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: User, 
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Update user with optional password hashing"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        return await super().update(db, db_obj=db_obj, obj_in=update_data)
    
    async def add_to_location(
        self, 
        db: AsyncSession, 
        *, 
        user_id: int, 
        location_id: int
    ) -> Optional[User]:
        """Add user to location"""
        from app.locations.models import Location
        
        query = (
            select(self.model)
            .options(
                selectinload(self.model.locations),
                selectinload(self.model.role).selectinload(Role.permissions)
            )
            .where(self.model.id == user_id)
        )
        result = await db.execute(query)
        user = result.scalars().first()
        
        if not user:
            return None
        
        query = select(Location).where(Location.id == location_id)
        result = await db.execute(query)
        location = result.scalars().first()
        
        if not location:
            return None
        
        if location not in user.locations:
            user.locations.append(location)
            await db.commit()
            await db.refresh(user)
            
            query = (
                select(self.model)
                .options(
                    selectinload(self.model.locations),
                    selectinload(self.model.role).selectinload(Role.permissions)
                )
                .where(self.model.id == user_id)
            )
            result = await db.execute(query)
            user = result.scalars().first()
        
        return user
    
    async def remove_from_location(
        self, 
        db: AsyncSession, 
        *, 
        user_id: int, 
        location_id: int
    ) -> Optional[User]:
        """Remove user from location"""
        from app.locations.models import Location
        
        user = await self.get_with_locations(db, id=user_id)
        if not user:
            return None
        
        query = select(Location).where(Location.id == location_id)
        result = await db.execute(query)
        location = result.scalars().first()
        
        if not location or location not in user.locations:
            return None
        
        user.locations.remove(location)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user 