from fastapi import APIRouter
from src.presentation.entities.auth_entities import (
    RegisterUserRequest,
    RegisterUserResponse,
    LoginUserRequest,
    LoginUserResponse,
    CheckTokenRequest,
    CheckTokenResponse
)
from src.logic.auth.authentication import register_user, login_user, check_user

user_router = APIRouter(prefix="/auth")


@user_router.post("/register", response_model=RegisterUserResponse)
async def register_user_handler(data: RegisterUserRequest):
    user_id = await register_user(username=data.username, password=data.password)
    return RegisterUserResponse(id=user_id, username=data.username)


@user_router.post("/login", response_model=LoginUserResponse)
async def login_user_handler(data: LoginUserRequest):
    token = await login_user(username=data.username, password=data.password)
    return LoginUserResponse(token=token)


@user_router.post("/check_token", response_model=CheckTokenResponse)
async def check_token_handler(data: CheckTokenRequest):
    user_id = await check_user(token=data.token)
    return CheckTokenResponse(user_id=user_id)
