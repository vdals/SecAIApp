from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, CurrentCameraManager, CurrentSuperuser
from app.common.schemas import PaginatedResult, PaginationParams
from app.db.session import get_db
from app.cameras.schemas import (
    Camera, CameraCreate, CameraUpdate, CameraWithLocation, CameraWithOwner, CameraFull, CameraStats
)
from app.cameras.service import CameraService
from app.users.models import User

router = APIRouter(prefix="/cameras", tags=["cameras"])

camera_service = CameraService()


@router.get("/", response_model=PaginatedResult[Camera], summary="Get list of cameras")
async def get_cameras(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(CurrentUser)]
) -> PaginatedResult[Camera]:
    """
    Get list of all cameras with pagination
    """
    return await camera_service.get_all(
        db, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/with-location", response_model=PaginatedResult[CameraWithLocation], summary="Get list of cameras with location information")
async def get_cameras_with_location(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> PaginatedResult[CameraWithLocation]:
    """
    Get list of all cameras with location information and pagination
    """
    return await camera_service.get_all_with_location(
        db, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/with-owner", response_model=PaginatedResult[CameraWithOwner], summary="Get list of cameras with owner information")
async def get_cameras_with_owner(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentCameraManager)]
) -> PaginatedResult[CameraWithOwner]:
    """
    Get list of all cameras with owner information and pagination
    (requires cameras.manage permission)
    """
    return await camera_service.get_all_with_owner(
        db, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/full", response_model=PaginatedResult[CameraFull], summary="Get list of cameras with full information")
async def get_cameras_full(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentCameraManager)]
) -> PaginatedResult[CameraFull]:
    """
    Get list of all cameras with full information and pagination
    (requires cameras.manage permission)
    """
    return await camera_service.get_all_full(
        db, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/location/{location_id}", response_model=PaginatedResult[Camera], summary="Get list of cameras by location")
async def get_cameras_by_location(
    location_id: int,
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> PaginatedResult[Camera]:
    """
    Get list of all cameras for a specific location with pagination
    """
    return await camera_service.get_all_by_location(
        db, location_id=location_id, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/my", response_model=PaginatedResult[Camera], summary="Get list of current user's cameras")
async def get_my_cameras(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(CurrentUser)]
) -> PaginatedResult[Camera]:
    """
    Get list of all current user's cameras with pagination
    """
    return await camera_service.get_all_by_owner(
        db, owner_id=current_user.id, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/{camera_id}", response_model=Camera, summary="Get camera by ID")
async def get_camera(
    camera_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> Camera:
    """
    Get camera by ID
    """
    camera = await camera_service.get_by_id(db, id=camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    return camera


@router.get("/{camera_id}/with-location", response_model=CameraWithLocation, summary="Get camera with location information")
async def get_camera_with_location(
    camera_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> CameraWithLocation:
    """
    Get camera with location information by ID
    """
    camera = await camera_service.get_with_location(db, id=camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    return camera


@router.get("/{camera_id}/with-owner", response_model=CameraWithOwner, summary="Get camera with owner information")
async def get_camera_with_owner(
    camera_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentCameraManager)]
) -> CameraWithOwner:
    """
    Get camera with owner information by ID
    (requires cameras.manage permission)
    """
    camera = await camera_service.get_with_owner(db, id=camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    return camera


@router.get("/{camera_id}/full", response_model=CameraFull, summary="Get camera with full information")
async def get_camera_full(
    camera_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentCameraManager)]
) -> CameraFull:
    """
    Get camera with full information by ID
    (requires cameras.manage permission)
    """
    camera = await camera_service.get_full(db, id=camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    return camera


@router.get("/{camera_id}/stats", response_model=CameraStats, summary="Get camera statistics")
async def get_camera_stats(
    camera_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> CameraStats:
    """
    Get camera statistics (number of videos, events, data volume)
    """
    stats = await camera_service.get_stats(db, id=camera_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    return stats


@router.post("/", response_model=CameraFull, status_code=status.HTTP_201_CREATED, summary="Create new camera")
async def create_camera(
    camera_in: CameraCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(CurrentCameraManager)]
) -> CameraFull:
    """
    Create new camera
    (requires cameras.manage permission)
    """
    try:
        return await camera_service.create(
            db, camera_in=camera_in, current_user_id=current_user.id
        )
    except (ValueError, NotFoundException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{camera_id}", response_model=CameraFull, summary="Update camera")
async def update_camera(
    camera_id: int,
    camera_in: CameraUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(CurrentUser)]
) -> CameraFull:
    """
    Update camera by ID
    (user must be owner of the camera or have cameras.manage permission)
    """
    try:
        camera = await camera_service.update(
            db, id=camera_id, camera_in=camera_in, current_user_id=current_user.id
        )
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Camera not found"
            )
        return camera
    except (ValueError, NotFoundException, ForbiddenException) as e:
        if isinstance(e, ForbiddenException):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete camera")
async def delete_camera(
    camera_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(CurrentUser)]
) -> None:
    """
    Delete camera by ID
    (user must be owner of the camera or have cameras.manage permission)
    """
    try:
        deleted = await camera_service.delete(
            db, id=camera_id, current_user_id=current_user.id
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Camera not found"
            )
    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        ) 