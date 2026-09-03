import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        x_request_id = request.headers.get("X-Request-Id")
        logger.contextualize(request_id=x_request_id or uuid.uuid4())
        response = await call_next(request)
        return response
