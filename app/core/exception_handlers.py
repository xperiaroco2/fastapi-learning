from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_CONTENT,
)

from app.core import EntityAlreadyExistsError, EntityNotFoundError, EntityUnauthorizedError


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def global_handler(request: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(EntityAlreadyExistsError)
    async def already_exists_handler(request: Request, exc: EntityAlreadyExistsError):
        return JSONResponse(status_code=HTTP_409_CONFLICT, content={"detail": exc.message})

    @app.exception_handler(EntityNotFoundError)
    async def not_found_handler(request: Request, exc: EntityNotFoundError):
        return JSONResponse(status_code=HTTP_404_NOT_FOUND, content={"detail": exc.message})

    @app.exception_handler(EntityUnauthorizedError)
    async def unauthorized_handler(request: Request, exc: EntityUnauthorizedError):
        return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={"detail": exc.message})

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation failed on {request.url.path}")
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "detail": "Validation error",
                "errors": jsonable_encoder(exc.errors()),
            },
        )
