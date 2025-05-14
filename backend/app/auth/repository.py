from typing import Optional, Union, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.models import Permission, Role
from app.auth.schemas import PermissionCreate, PermissionUpdate, RoleCreate, RoleUpdate
from app.common.repository import BaseRepository


class PermissionRepository(BaseRepository[Permission, PermissionCreate, PermissionUpdate]):
    """Repository for working with permissions"""
    
    def __init__(self):
        super().__init__(Permission)

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Permission]:
        """Get permission by name"""
        query = select(self.model).where(self.model.name == name)
        result = await db.execute(query)
        return result.scalars().first()


class RoleRepository(BaseRepository[Role, RoleCreate, RoleUpdate]):
    """Repository for working with roles"""
    
    def __init__(self):
        super().__init__(Role)

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Role]:
        """Get role by name"""
        query = select(self.model).where(self.model.name == name)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_with_permissions(self, db: AsyncSession, role_id: int) -> Optional[Role]:
        """Get role with permissions"""
        query = (
            select(self.model)
            .options(selectinload(self.model.permissions))
            .where(self.model.id == role_id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def create(self, db: AsyncSession, *, obj_in: RoleCreate) -> Role:
        """Create role with permissions"""
        permissions = []
        permission_ids = obj_in.permission_ids or []
        
        if permission_ids:
            query = select(Permission).where(Permission.id.in_(permission_ids))
            result = await db.execute(query)
            permissions = result.scalars().all()
        
        role_data = obj_in.dict(exclude={"permission_ids"})
        db_obj = Role(**role_data)
        db_obj.permissions = permissions
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: Role, 
        obj_in: Union[RoleUpdate, Dict[str, Any]]
    ) -> Role:
        """Update role with permissions"""
        if isinstance(obj_in, dict):
            update_data = obj_in
            permission_ids = update_data.pop("permission_ids", None)
        else:
            update_data = obj_in.dict(exclude_unset=True, exclude={"permission_ids"})
            permission_ids = obj_in.permission_ids

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        if permission_ids is not None:
            query = select(Permission).where(Permission.id.in_(permission_ids))
            result = await db.execute(query)
            permissions = result.scalars().all()
            db_obj.permissions = permissions
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj 