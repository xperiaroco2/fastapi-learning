from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class CatchAllExceptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.error(
                f"System crash on {request.method} {request.url.path}:"
                f"{exc.__class__.__name__} - {str(exc)}"
            )

            return JSONResponse(
                status_code=500, content={"detail": "Internal Server Error"}
            )
