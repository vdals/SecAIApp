from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import PaginatedResult
from app.locations.models import Location
from app.locations.repository import LocationRepository
from app.locations.schemas import (
    Location as LocationSchema,
    LocationCreate, 
    LocationUpdate,
    LocationWithUsers,
    LocationWithCameras,
    LocationFull
)


class LocationService:
    """Service for working with locations"""
    
    def __init__(self, repository: LocationRepository = LocationRepository()):
        self.repository = repository
    
    async def get_all(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[LocationSchema]:
        """Get all locations with pagination"""
        locations = await self.repository.get_all(db, skip=skip, limit=limit)
        total = await self.repository.count(db)
        
        location_dicts = [self._model_to_dict(loc) for loc in locations]
        
        return PaginatedResult.create(
            items=[LocationSchema.model_validate(loc) for loc in location_dicts],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_all_with_users(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[LocationWithUsers]:
        """Get all locations with users and pagination"""
        locations = await self.repository.get_all_with_users(db, skip=skip, limit=limit)
        total = await self.repository.count(db)
        
        location_dicts = [self._model_to_dict(loc) for loc in locations]
        
        return PaginatedResult.create(
            items=[LocationWithUsers.model_validate(loc) for loc in location_dicts],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_all_with_cameras(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> PaginatedResult[LocationWithCameras]:
        """Get all locations with cameras and pagination"""
        locations = await self.repository.get_all_with_cameras(db, skip=skip, limit=limit)
        total = await self.repository.count(db)
        
        location_dicts = [self._model_to_dict(loc) for loc in locations]
        
        return PaginatedResult.create(
            items=[LocationWithCameras.model_validate(loc) for loc in location_dicts],
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
    ) -> PaginatedResult[LocationFull]:
        """Get all locations with users, cameras and pagination"""
        locations = await self.repository.get_all_full(db, skip=skip, limit=limit)
        total = await self.repository.count(db)
        
        location_dicts = [self._model_to_dict(loc) for loc in locations]
        
        return PaginatedResult.create(
            items=[LocationFull.model_validate(loc) for loc in location_dicts],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_by_id(self, db: AsyncSession, *, id: int) -> Optional[LocationSchema]:
        """Get location by ID"""
        location = await self.repository.get(db, id=id)
        if not location:
            return None
        
        location_dict = self._model_to_dict(location)
        return LocationSchema.model_validate(location_dict)
    
    async def get_with_users(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[LocationWithUsers]:
        """Get location with users by ID"""
        location = await self.repository.get_with_users(db, id=id)
        if not location:
            return None
        
        location_dict = self._model_to_dict(location)
        return LocationWithUsers.model_validate(location_dict)
    
    async def get_with_cameras(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[LocationWithCameras]:
        """Get location with cameras by ID"""
        location = await self.repository.get_with_cameras(db, id=id)
        if not location:
            return None
        
        location_dict = self._model_to_dict(location)
        return LocationWithCameras.model_validate(location_dict)
    
    async def get_full(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[LocationFull]:
        """Get location with users and cameras by ID"""
        location = await self.repository.get_full(db, id=id)
        if not location:
            return None
        
        location_dict = self._model_to_dict(location)
        return LocationFull.model_validate(location_dict)
    
    async def create(
        self, 
        db: AsyncSession, 
        *, 
        location_in: LocationCreate
    ) -> LocationSchema:
        """Create location"""
        location = await self.repository.create(db, obj_in=location_in)
        
        location_dict = self._model_to_dict(location)
        return LocationSchema.model_validate(location_dict)
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        location_in: LocationUpdate
    ) -> Optional[LocationSchema]:
        """Update location"""
        location = await self.repository.get(db, id=id)
        if not location:
            return None
        
        updated_location = await self.repository.update(
            db, db_obj=location, obj_in=location_in
        )
        
        location_dict = self._model_to_dict(updated_location)
        return LocationSchema.model_validate(location_dict)
    
    async def delete(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> bool:
        """Delete location"""
        return await self.repository.delete(db, id=id)
        
    def _model_to_dict(self, model: Location) -> Dict[str, Any]:
        """Convert SQLAlchemy model to dictionary with nested objects"""
        result = {}
        for key in model.__dict__:
            if not key.startswith('_'):
                value = getattr(model, key)
                
                if key == 'users' and value:
                    # Convert list of users
                    users = []
                    for user in value:
                        users.append({
                            'id': user.id,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'is_active': user.is_active,
                            'role_id': user.role_id,
                            'created_at': user.created_at,
                            'updated_at': user.updated_at
                        })
                    result[key] = users
                
                elif key == 'cameras' and value:
                    # Convert list of cameras
                    cameras = []
                    for camera in value:
                        cameras.append({
                            'id': camera.id,
                            'name': camera.name,
                            'ip_address': camera.ip_address,
                            'rtsp_url': camera.rtsp_url,
                            'description': camera.description,
                            'is_active': camera.is_active,
                            'location_id': camera.location_id,
                            'owner_id': camera.owner_id,
                            'resolution_width': camera.resolution_width,
                            'resolution_height': camera.resolution_height,
                            'fps': camera.fps,
                            'rotation': camera.rotation,
                            'timezone': camera.timezone,
                            'created_at': camera.created_at,
                            'updated_at': camera.updated_at
                        })
                    result[key] = cameras
                
                else:
                    result[key] = value
                    
        return result 