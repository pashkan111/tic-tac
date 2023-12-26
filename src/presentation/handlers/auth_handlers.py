from fastapi import APIRouter
from src.presentation.entities.auth_entities import RegisterUserRequest, RegisterUserResponse
from src.logic.auth.authentication import register_user

user_router = APIRouter(prefix='/auth')


@user_router.post('/register', response_model=RegisterUserResponse)
async def register_user_handler(data: RegisterUserRequest):
    user_id = await register_user(
        username=data.username, password=data.password
    )
    return RegisterUserResponse(
        id=user_id, username=data.username
    )
