import pydantic as pd


class RegisterUserRequest(pd.BaseModel):
    username: str
    password: str


class RegisterUserResponse(pd.BaseModel):
    id: int
    username: str


class LoginUserRequest(pd.BaseModel):
    username: str
    password: str


class LoginUserResponse(pd.BaseModel):
    token: str


class CheckTokenRequest(pd.BaseModel):
    token: str


class CheckTokenResponse(pd.BaseModel):
    user_id: int
