from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentSuperuser, CurrentUser, RequirePermission
from app.common.schemas import PaginatedResult, PaginationParams
from app.db.session import get_db
from app.users.models import User
from app.users.schemas import (
    User as UserSchema, UserCreate, UserUpdate, UserWithLocations, UserChangePassword
)
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])

user_service = UserService()


@router.get("/", response_model=PaginatedResult[UserSchema], summary="Get list of users")
async def get_users(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> PaginatedResult[UserSchema]:
    """
    Get list of all users (only for admins)
    """
    return await user_service.get_all(
        db, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/me", response_model=UserSchema, summary="Get information about current user")
async def get_current_user_info(
    current_user: Annotated[User, Depends(CurrentUser)]
) -> UserSchema:
    """
    Get information about current user
    """
    return UserSchema.model_validate(current_user)


@router.get("/me/locations", response_model=UserWithLocations, summary="Get locations of current user")
async def get_current_user_locations(
    current_user: Annotated[User, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserWithLocations:
    """
    Get information about current user with its locations
    """
    user = await user_service.get_with_locations(db, id=current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/{user_id}", response_model=UserSchema, summary="Get user by ID")
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> UserSchema:
    """
    Get user by ID (only for admins)
    """
    user = await user_service.get_by_id(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED, summary="Create new user")
async def create_user(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> UserSchema:
    """
    Create new user (only for admins)
    """
    try:
        return await user_service.create(db, user_in=user_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/me", response_model=UserSchema, summary="Update current user")
async def update_current_user(
    user_in: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(CurrentUser)]
) -> UserSchema:
    """
    Update current user profile
    """
    try:
        updated_user = await user_service.update(db, id=current_user.id, user_in=user_in)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=UserSchema, summary="Update user")
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> UserSchema:
    """
    Update user by ID (only for admins)
    """
    try:
        user = await user_service.update(db, id=user_id, user_in=user_in)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user")
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> None:
    """
    Delete user by ID (only for admins)
    """
    deleted = await user_service.delete(db, id=user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.post("/me/change-password", response_model=UserSchema, summary="Change current user password")
async def change_current_user_password(
    password_data: UserChangePassword,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(CurrentUser)]
) -> UserSchema:
    """
    Change current user password
    """
    try:
        user = await user_service.change_password(
            db, 
            id=current_user.id, 
            current_password=password_data.current_password, 
            new_password=password_data.new_password
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{user_id}/locations/{location_id}", response_model=UserWithLocations, summary="Add user to location")
async def add_user_to_location(
    user_id: int,
    location_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(RequirePermission("locations.manage"))]
) -> UserWithLocations:
    """
    Add user to location (requires locations.manage permission)
    """
    user = await user_service.add_to_location(
        db, user_id=user_id, location_id=location_id
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or location not found"
        )
    return user


@router.delete("/{user_id}/locations/{location_id}", response_model=UserWithLocations, summary="Remove user from location")
async def remove_user_from_location(
    user_id: int,
    location_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(RequirePermission("locations.manage"))]
) -> UserWithLocations:
    """
    Remove user from location (requires locations.manage permission)
    """
    user = await user_service.remove_from_location(
        db, user_id=user_id, location_id=location_id
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or location not found or user is not assigned to this location"
        )
    return user 