from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth import (
    Token,
    User,
    UserCreate,
    UserInDB,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    verify_password,
)


router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


def _state(request: Request) -> dict[str, Any]:
    return request.app.state.app_state


@router.post("/register", status_code=201)
@limiter.limit("5/minute")
async def register(user_data: UserCreate, request: Request) -> UserInDB:
    users = _state(request).setdefault("users", {})

    if any(user.get("email") == str(user_data.email) for user in users.values()):
        raise HTTPException(status_code=400, detail="Email already registered")

    if any(user.get("username") == user_data.username for user in users.values()):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = UserInDB(
        id=f"user_{uuid4().hex[:12]}",
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=True,
        created_at=datetime.now(UTC),
        hashed_password=get_password_hash(user_data.password),
    )
    users[user.id] = json.loads(user.model_dump_json())
    request.app.state.persist_state()
    return user


@router.post("/login")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    users = _state(request).get("users", {})
    user = next(
        (
            candidate
            for candidate in users.values()
            if candidate.get("username") == form_data.username
            or candidate.get("email") == form_data.username
        ),
        None,
    )

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="User account is disabled")

    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=timedelta(minutes=30),
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me")
async def get_me(request: Request, current_user: dict = Depends(get_current_active_user)) -> User:
    users = _state(request).get("users", {})
    for user in users.values():
        if user.get("username") == current_user.username:
            return User(**user)
    raise HTTPException(status_code=404, detail="User not found")
