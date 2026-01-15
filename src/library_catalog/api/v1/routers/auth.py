from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

from src.library_catalog.core.config import settings

router = APIRouter(prefix="/api/v1", tags=["auth"])

@router.post("/token")
async def login_for_access_token(
    form: OAuth2PasswordRequestForm = Depends()
):
    expire = datetime.utcnow() + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )

    token = jwt.encode(
        {
            "sub": form.username,
            "exp": expire
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return {"access_token": token, "token_type": "bearer"}
