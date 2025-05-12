"""
Dependency functions for authentication components
"""
from typing import Annotated, Optional
import logging

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import TokenPayload
from app.config import settings
from app.db.session import get_db
from app.users.models import User
from app.users.service import UserService
from app.auth.models import Permission

logger = logging.getLogger(__name__)

user_service = UserService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login/form")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user by token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.info(f"Decoding token: {token[:10]}...")
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        logger.info(f"Token payload: {payload}")
        user_id: Optional[int] = int(payload.get("sub"))
        if user_id is None:
            logger.error("User ID is missing from token")
            raise credentials_exception
        logger.info(f"User ID: {user_id}")
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (JWTError, TypeError, ValueError) as e:
        logger.error(f"Error decoding token: {str(e)}")
        raise credentials_exception
    
    user = await user_service.get_by_id(db, id=user_id)
    if user is None:
        logger.error(f"User with ID {user_id} not found")
        raise credentials_exception
    logger.info(f"User found: {user.email}")
    return user


async def get_current_active_user(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> User:
    """Check if current user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def has_permission(
    permission_name: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Check if user has specified permission"""
    logger.info(f"Checking permission '{permission_name}' for user {current_user.id}")
    user = await user_service.get_with_role(db, id=current_user.id)
    if not user or not user.role:
        logger.error(f"User {current_user.id} has no role")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no role"
        )
    
    logger.info(f"User role: {user.role.name}")
    
    permission_mapping = {
    "manage_locations": "locations.manage",
    "manage_events": "events.manage",
    "manage_cameras": "cameras.manage",
    "manage_videos": "videos.manage",
}
    db_permission_name = permission_mapping.get(permission_name, permission_name)
    
    logger.info(f"Looking for permission: '{db_permission_name}'")
    
    # Check if user has permission
    permissions = [p.name for p in user.role.permissions]
    logger.info(f"User permissions: {permissions}")
    
    if db_permission_name in permissions or "all" in permissions or user.role.name == "admin":
        logger.info(f"User {user.id} has permission '{db_permission_name}'")
        return user
    
    logger.warning(f"User {user.id} does not have permission '{db_permission_name}'")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"No permission: {permission_name}"
    )


async def get_superuser(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Check if user is superuser"""
    return await has_permission("superuser", current_user, db)

CurrentUser = get_current_active_user
CurrentSuperuser = get_superuser


def RequirePermission(permission_name: str):
    """Create a dependency function to check permission"""
    async def check_permission(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: Annotated[AsyncSession, Depends(get_db)]
    ) -> User:
        return await has_permission(permission_name, current_user, db)
    return check_permission


async def get_event_manager(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Check if user has permission to manage events"""
    return await has_permission("manage_events", current_user, db)

async def get_location_manager(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Check if user has permission to manage locations"""
    return await has_permission("manage_locations", current_user, db)

async def get_camera_manager(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Check if user has permission to manage cameras"""
    return await has_permission("manage_cameras", current_user, db)

async def get_video_manager(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Check if user has permission to manage videos"""
    return await has_permission("manage_videos", current_user, db)

CurrentEventManager = get_event_manager
CurrentLocationManager = get_location_manager
CurrentCameraManager = get_camera_manager
CurrentVideoManager = get_video_manager