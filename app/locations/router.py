from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, CurrentLocationManager, CurrentSuperuser
from app.common.schemas import PaginatedResult, PaginationParams
from app.db.session import get_db
from app.locations.schemas import (
    Location, LocationCreate, LocationUpdate, LocationWithUsers, LocationWithCameras, LocationFull
)
from app.locations.service import LocationService
from app.users.models import User

router = APIRouter(prefix="/locations", tags=["locations"])

location_service = LocationService()


@router.get("/", response_model=PaginatedResult[Location], summary="Get list of locations")
async def get_locations(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(CurrentUser)]
) -> PaginatedResult[Location]:
    """
    Get list of all locations with pagination
    """
    return await location_service.get_all(
        db, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/with-users", response_model=PaginatedResult[LocationWithUsers], summary="Get list of locations with users")
async def get_locations_with_users(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentLocationManager)]
) -> PaginatedResult[LocationWithUsers]:
    """
    Get list of all locations with users and pagination
    (requires locations.manage permission)
    """
    return await location_service.get_all_with_users(
        db, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/with-cameras", response_model=PaginatedResult[LocationWithCameras], summary="Get list of locations with cameras")
async def get_locations_with_cameras(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentLocationManager)]
) -> PaginatedResult[LocationWithCameras]:
    """
    Get list of all locations with cameras and pagination
    (requires locations.manage permission)
    """
    return await location_service.get_all_with_cameras(
        db, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/full", response_model=PaginatedResult[LocationFull], summary="Get list of locations with users and cameras")
async def get_locations_full(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentLocationManager)]
) -> PaginatedResult[LocationFull]:
    """
    Get list of all locations with users, cameras and pagination
    (requires locations.manage permission)
    """
    return await location_service.get_all_full(
        db, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/{location_id}", response_model=Location, summary="Get location by ID")
async def get_location(
    location_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> Location:
    """
    Get location by ID
    """
    location = await location_service.get_by_id(db, id=location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return location


@router.get("/{location_id}/with-users", response_model=LocationWithUsers, summary="Get location with users")
async def get_location_with_users(
    location_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentLocationManager)]
) -> LocationWithUsers:
    """
    Get location with users by ID
    (requires locations.manage permission)
    """
    location = await location_service.get_with_users(db, id=location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return location


@router.get("/{location_id}/with-cameras", response_model=LocationWithCameras, summary="Get location with cameras")
async def get_location_with_cameras(
    location_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentLocationManager)]
) -> LocationWithCameras:
    """
    Get location with cameras by ID
    (requires locations.manage permission)
    """
    location = await location_service.get_with_cameras(db, id=location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return location


@router.get("/{location_id}/full", response_model=LocationFull, summary="Get location with users and cameras")
async def get_location_full(
    location_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentLocationManager)]
) -> LocationFull:
    """
    Get location with users and cameras by ID
    (requires locations.manage permission)
    """
    location = await location_service.get_full(db, id=location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return location


@router.post("/", response_model=Location, status_code=status.HTTP_201_CREATED, summary="Create new location")
async def create_location(
    location_in: LocationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentLocationManager)]
) -> Location:
    """
    Create new location
    (requires locations.manage permission)
    """
    return await location_service.create(db, location_in=location_in)


@router.put("/{location_id}", response_model=Location, summary="Update location")
async def update_location(
    location_id: int,
    location_in: LocationUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentLocationManager)]
) -> Location:
    """
    Update location by ID
    (requires locations.manage permission)
    """
    location = await location_service.update(db, id=location_id, location_in=location_in)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete location")
async def delete_location(
    location_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentLocationManager)]
) -> None:
    """
    Delete location by ID
    (requires locations.manage permission)
    """
    deleted = await location_service.delete(db, id=location_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        ) 