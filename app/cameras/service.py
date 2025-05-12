from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import PaginatedResult
from app.cameras.models import Camera
from app.cameras.repository import CameraRepository
from app.cameras.schemas import (
    Camera as CameraSchema,
    CameraCreate, 
    CameraUpdate,
    CameraWithLocation,
    CameraWithOwner,
    CameraFull,
    CameraStats
)
from app.locations.repository import LocationRepository
from app.users.repository import UserRepository
from app.common.utils import NotFoundException, ForbiddenException


class CameraService:
    """Service for working with cameras"""
    
    def __init__(
        self, 
        repository: CameraRepository = CameraRepository(),
        location_repository: LocationRepository = LocationRepository(),
        user_repository: UserRepository = UserRepository()
    ):
        self.repository = repository
        self.location_repository = location_repository
        self.user_repository = user_repository
    
    async def get_all(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[CameraSchema]:
        """Get all cameras with pagination"""
        cameras = await self.repository.get_all(db, skip=skip, limit=limit)
        total = await self.repository.count(db)
        
        camera_dicts = [self._model_to_dict(c) for c in cameras]
        
        return PaginatedResult.create(
            items=[CameraSchema.model_validate(c) for c in camera_dicts],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_all_by_location(
        self, 
        db: AsyncSession, 
        *, 
        location_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[CameraSchema]:
        """Get all cameras for a specific location with pagination"""
        cameras = await self.repository.get_all_by_location(
            db, location_id=location_id, skip=skip, limit=limit
        )
        total = await self.repository.count(
            db, filters={"location_id": location_id}
        )
        
        camera_dicts = [self._model_to_dict(c) for c in cameras]
        
        return PaginatedResult.create(
            items=[CameraSchema.model_validate(c) for c in camera_dicts],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_all_by_owner(
        self, 
        db: AsyncSession, 
        *, 
        owner_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[CameraSchema]:
        """Get all cameras for a specific owner with pagination"""
        cameras = await self.repository.get_all_by_owner(
            db, owner_id=owner_id, skip=skip, limit=limit
        )
        total = await self.repository.count(
            db, filters={"owner_id": owner_id}
        )
        
        camera_dicts = [self._model_to_dict(c) for c in cameras]
        
        return PaginatedResult.create(
            items=[CameraSchema.model_validate(c) for c in camera_dicts],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_all_with_location(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[CameraWithLocation]:
        """Get all cameras with location information and pagination"""
        cameras = await self.repository.get_all_with_location(db, skip=skip, limit=limit)
        total = await self.repository.count(db)
        
        camera_dicts = [self._model_to_dict(c) for c in cameras]
        
        return PaginatedResult.create(
            items=[CameraWithLocation.model_validate(c) for c in camera_dicts],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_all_with_owner(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[CameraWithOwner]:
        """Get all cameras with owner information and pagination"""
        cameras = await self.repository.get_all_with_owner(db, skip=skip, limit=limit)
        total = await self.repository.count(db)
        
        camera_dicts = [self._model_to_dict(c) for c in cameras]
        
        return PaginatedResult.create(
            items=[CameraWithOwner.model_validate(c) for c in camera_dicts],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_all_full(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[CameraFull]:
        """Get all cameras with location, owner information and pagination"""
        cameras = await self.repository.get_all_full(db, skip=skip, limit=limit)
        total = await self.repository.count(db)
        
        camera_dicts = [self._model_to_dict(c) for c in cameras]
        
        return PaginatedResult.create(
            items=[CameraFull.model_validate(c) for c in camera_dicts],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_by_id(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[CameraSchema]:
        """Get camera by ID"""
        camera = await self.repository.get(db, id=id)
        if not camera:
            return None
        camera_dict = self._model_to_dict(camera)
        return CameraSchema.model_validate(camera_dict)
    
    async def get_with_location(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[CameraWithLocation]:
        """Get camera with location information by ID"""
        camera = await self.repository.get_with_location(db, id=id)
        if not camera:
            return None
        camera_dict = self._model_to_dict(camera)
        return CameraWithLocation.model_validate(camera_dict)
    
    async def get_with_owner(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[CameraWithOwner]:
        """Get camera with owner information by ID"""
        camera = await self.repository.get_with_owner(db, id=id)
        if not camera:
            return None
        camera_dict = self._model_to_dict(camera)
        return CameraWithOwner.model_validate(camera_dict)
    
    async def get_full(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[CameraFull]:
        """Get camera with location and owner information by ID"""
        camera = await self.repository.get_full(db, id=id)
        if not camera:
            return None
        camera_dict = self._model_to_dict(camera)
        return CameraFull.model_validate(camera_dict)
    
    async def create(
        self, 
        db: AsyncSession, 
        *, 
        camera_in: CameraCreate,
        current_user_id: int
    ) -> CameraFull:
        """Create a camera"""
        location = await self.location_repository.get(db, id=camera_in.location_id)
        if not location:
            raise NotFoundException(f"Location with ID {camera_in.location_id} not found")
        
        # Если owner_id не указан, используем текущего пользователя
        if camera_in.owner_id is None:
            camera_in.owner_id = current_user_id
        else:
            owner = await self.user_repository.get(db, id=camera_in.owner_id)
            if not owner:
                raise NotFoundException(f"User with ID {camera_in.owner_id} not found")
        
        camera = await self.repository.create(db, obj_in=camera_in)
        
        camera_full = await self.repository.get_full(db, id=camera.id)
        camera_dict = self._model_to_dict(camera_full)
        return CameraFull.model_validate(camera_dict)
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        camera_in: CameraUpdate,
        current_user_id: int
    ) -> Optional[CameraFull]:
        """Update a camera"""
        camera = await self.repository.get(db, id=id)
        if not camera:
            return None
        
        if camera.owner_id != current_user_id:
            raise ForbiddenException("You don't have permission to update this camera")
        
        if camera_in.location_id is not None:
            location = await self.location_repository.get(db, id=camera_in.location_id)
            if not location:
                raise NotFoundException(f"Location with ID {camera_in.location_id} not found")
        
        if camera_in.owner_id is not None:
            owner = await self.user_repository.get(db, id=camera_in.owner_id)
            if not owner:
                raise NotFoundException(f"User with ID {camera_in.owner_id} not found")
        
        updated_camera = await self.repository.update(db, db_obj=camera, obj_in=camera_in)
        
        camera_full = await self.repository.get_full(db, id=updated_camera.id)
        camera_dict = self._model_to_dict(camera_full)
        return CameraFull.model_validate(camera_dict)
    
    async def delete(
        self, 
        db: AsyncSession, 
        *, 
        id: int,
        current_user_id: int
    ) -> bool:
        """Delete a camera"""
        camera = await self.repository.get(db, id=id)
        if not camera:
            return False
        
        if camera.owner_id != current_user_id:
            raise ForbiddenException("You don't have permission to delete this camera")
        
        return await self.repository.delete(db, id=id)
    
    async def get_stats(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[CameraStats]:
        """Get statistics for a camera"""
        camera = await self.repository.get(db, id=id)
        if not camera:
            return None
        
        return await self.repository.get_stats(db, camera_id=id)
    
    def _model_to_dict(self, model: Camera) -> Dict[str, Any]:
        """Convert SQLAlchemy model to dictionary with full conversion of nested objects"""
        result = {}
        for key in model.__dict__:
            if not key.startswith('_'):
                value = getattr(model, key)
                if key == 'location' and value is not None:
                    location_dict = {
                        'id': value.id,
                        'name': value.name,
                        'address': value.address,
                        'description': value.description,
                        'latitude': value.latitude,
                        'longitude': value.longitude,
                        'created_at': value.created_at,
                        'updated_at': value.updated_at
                    }
                    result[key] = location_dict
                elif key == 'owner' and value is not None:
                    owner_dict = {
                        'id': value.id,
                        'email': value.email,
                        'first_name': value.first_name,
                        'last_name': value.last_name,
                        'is_active': value.is_active,
                        'role_id': value.role_id,
                        'created_at': value.created_at,
                        'updated_at': value.updated_at
                    }
                    result[key] = owner_dict
                else:
                    result[key] = value
        return result 