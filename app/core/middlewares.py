import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        raw = request.headers.get("X-Request-Id")
        try:
            request_id = uuid.UUID(raw) if raw else uuid.uuid4()
        except ValueError:
            request_id = uuid.uuid4()

        request_id = str(request_id)

        with logger.contextualize(request_id=request_id):
            response = await call_next(request)
            response.headers["X-Request-Id"] = request_id
            return response
