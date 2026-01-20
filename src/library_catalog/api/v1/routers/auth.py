# src/library_catalog/api/v1/routers/auth.py
"""Authentication routes with proper password verification."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from ....core.auth import create_access_token, get_password_hash, verify_password
from ....data.models.user import User
from ....data.repositories.user_repository import UserRepository
from ...dependencies import DbSessionDep

router = APIRouter(prefix="/auth", tags=["Authentication"])


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    """User registration model."""
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model."""
    user_id: str
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True


async def get_user_repository(db: DbSessionDep) -> UserRepository:
    """Get user repository."""
    return UserRepository(db)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]


async def authenticate_user(
        username: str,
        password: str,
        user_repo: UserRepository,
) -> User | None:
    """
    Authenticate a user by username and password.

    Args:
        username: Username to authenticate
        password: Plain text password
        user_repo: User repository

    Returns:
        User object if authentication successful, None otherwise
    """
    user = await user_repo.find_by_username(username)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        user_data: UserCreate,
        user_repo: UserRepoDep,
        db: DbSessionDep,
):
    """
    Register a new user.

    This endpoint creates a new user account with hashed password.
    """
    # Check if username already exists
    existing_user = await user_repo.find_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = await user_repo.find_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user
    user = await user_repo.create(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
    )

    # Commit transaction
    await db.commit()

    return UserResponse(
        user_id=str(user.user_id),
        username=user.username,
        email=user.email,
        is_active=user.is_active,
    )


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_repo: UserRepoDep,
):
    """
    Login endpoint to get JWT access token.

    OAuth2 compatible token endpoint. Use username and password to get a JWT token.

    Raises:
        HTTPException 401: If credentials are invalid
    """
    user = await authenticate_user(form_data.username, form_data.password, user_repo)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": str(user.user_id),
            "email": user.email,
        }
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
        current_user: Annotated[User, Depends(lambda: None)],  # Будет заменено на get_current_user
):
    """
    Get current authenticated user info.

    Requires valid JWT token in Authorization header.
    """
    return UserResponse(
        user_id=str(current_user.user_id),
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
    )