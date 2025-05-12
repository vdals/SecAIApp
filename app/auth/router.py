from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    CurrentSuperuser, CurrentUser, has_permission
)
from app.auth.schemas import (
    Login, Permission, PermissionCreate, PermissionUpdate,
    RefreshToken, Role, RoleCreate, RoleUpdate, Token
)
from app.auth.service import AuthService, PermissionService, RoleService
from app.common.schemas import PaginationParams
from app.db.session import get_db
from app.users.models import User
from app.users.schemas import User as UserSchema, UserCreate
from app.common.utils import UnauthorizedException
from app.users.service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = AuthService()
permission_service = PermissionService()
role_service = RoleService()


@router.post("/login", response_model=Token, summary="Login user through form")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """
    Login user through form and get JWT tokens
    """
    user = await auth_service.authenticate_user(
        db, form_data.username, form_data.password
    )
    
    if not user:
        raise UnauthorizedException("Incorrect email or password")
    
    return await auth_service.create_token(user.id)


@router.post("/login/json", response_model=Token, summary="Login through JSON")
async def login_json(
    login_data: Login,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """
    Login user through JSON and get JWT tokens
    """
    user = await auth_service.authenticate_user(
        db, login_data.email, login_data.password
    )
    
    if not user:
        raise UnauthorizedException("Incorrect email or password")
    
    return await auth_service.create_token(user.id)


@router.post("/login/form", response_model=Token, summary="Login user through form (for Swagger UI)")
async def login_form(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """
    Login user through form and get JWT tokens.
    """
    user = await auth_service.authenticate_user(
        db, form_data.username, form_data.password
    )
    
    if not user:
        raise UnauthorizedException("Incorrect email or password")
    
    return await auth_service.create_token(user.id)


@router.post("/refresh", response_model=Token, summary="Refresh token")
async def refresh(
    refresh_token: RefreshToken,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """
    Refresh JWT token using refresh token
    """
    return await auth_service.refresh_token(db, refresh_token.refresh_token)


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED, summary="Register new user")
async def register(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserSchema:
    """
    Register new user
    """
    try:
        return await auth_service.register_user(db, user_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=UserSchema, summary="Get current user information")
async def get_current_user_info(
    current_user: Annotated[User, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserSchema:
    """
    Get current user information
    """
    user_service = UserService()
    user_with_role = await user_service.get_with_role(db, id=current_user.id)
    if not user_with_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user_with_role


# Routes for permissions (only for admins)
@router.get("/permissions", response_model=List[Permission], summary="Get all permissions")
async def get_permissions(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> List[Permission]:
    """
    Get all permissions
    """
    return await permission_service.get_all(
        db, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/permissions/{permission_id}", response_model=Permission, summary="Get permission by ID")
async def get_permission(
    permission_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> Permission:
    """
    Get permission by ID
    """
    permission = await permission_service.get_by_id(db, id=permission_id)
    
    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return permission


@router.post("/permissions", response_model=Permission, status_code=status.HTTP_201_CREATED, summary="Create new permission")
async def create_permission(
    permission_in: PermissionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> Permission:
    """
    Create new permission
    """
    return await permission_service.create(db, permission_in=permission_in)


@router.put("/permissions/{permission_id}", response_model=Permission, summary="Update permission")
async def update_permission(
    permission_id: int,
    permission_in: PermissionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> Permission:
    """
    Update permission by ID
    """
    permission = await permission_service.update(
        db, id=permission_id, permission_in=permission_in
    )
    
    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return permission


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete permission")
async def delete_permission(
    permission_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> None:
    """
    Delete permission by ID
    """
    deleted = await permission_service.delete(db, id=permission_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )


# Routes for roles (only for admins)
@router.get("/roles", response_model=List[Role], summary="Get all roles")
async def get_roles(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> List[Role]:
    """
    Get all roles
    """
    return await role_service.get_all(
        db, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/roles/{role_id}", response_model=Role, summary="Get role by ID")
async def get_role(
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> Role:
    """
    Get role by ID
    """
    role = await role_service.get_by_id(db, id=role_id)
    
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return role


@router.post("/roles", response_model=Role, status_code=status.HTTP_201_CREATED, summary="Create new role")
async def create_role(
    role_in: RoleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> Role:
    """
    Create new role
    """
    return await role_service.create(db, role_in=role_in)


@router.put("/roles/{role_id}", response_model=Role, summary="Update role")
async def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> Role:
    """
    Update role by ID
    """
    role = await role_service.update(db, id=role_id, role_in=role_in)
    
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete role")
async def delete_role(
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentSuperuser)]
) -> None:
    """
    Delete role by ID
    """
    deleted = await role_service.delete(db, id=role_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        ) 