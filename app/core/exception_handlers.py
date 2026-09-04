from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_CONTENT,
)

from app.core.exceptions import BaseAuthError, EntityAlreadyExistsError, EntityNotFoundError
from app.core.logger import logger


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("unhandled_error", method=request.method, path=request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

    @app.exception_handler(EntityAlreadyExistsError)
    async def already_exists_handler(request: Request, exc: EntityAlreadyExistsError):
        return JSONResponse(status_code=HTTP_409_CONFLICT, content={"detail": exc.message})

    @app.exception_handler(EntityNotFoundError)
    async def not_found_handler(request: Request, exc: EntityNotFoundError):
        return JSONResponse(status_code=HTTP_404_NOT_FOUND, content={"detail": exc.message})

    @app.exception_handler(BaseAuthError)
    async def unauthorized_handler(request: Request, exc: BaseAuthError):
        return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={"detail": exc.message})

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        logger.warning("validation_failed", path=request.url.path)
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "detail": "Validation error",
                "errors": jsonable_encoder(exc.errors()),
            },
        )
