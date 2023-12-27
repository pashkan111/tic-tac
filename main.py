from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.presentation.handlers.auth_handlers import user_router

# from fastapi.responses import JSONResponse
# from fastapi.exceptions import RequestValidationError


# @app.exception_handler(RequestValidationError)
# async def custom_exception_handler(request, exc: RequestValidationError):
#     response = MainResponse(data=None, error=exc.errors(), status=400)
#     return JSONResponse(content=response.model_dump(), status_code=400)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.repo.repository_common import pg

    await pg.create_pool()
    yield
    # Clean up the ML models and release the resources


app = FastAPI(lifespan=lifespan)


app.include_router(user_router)
