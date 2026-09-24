from functools import wraps

from groq import APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError
from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError

from app.core.exceptions import AnalyseFailedError


def handle_llm_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (OutputParserException, ValidationError) as exc:
            raise AnalyseFailedError("invalid_output") from exc
        except (RateLimitError, APITimeoutError, APIConnectionError) as exc:
            raise AnalyseFailedError("unavailable") from exc
        except AuthenticationError as exc:
            raise AnalyseFailedError("rejected") from exc
        except Exception as exc:
            raise AnalyseFailedError("unknown_error") from exc

    return wrapper
