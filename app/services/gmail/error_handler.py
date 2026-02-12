"""
Centralized Error Handling and Retry Logic
------------------------------------------
Provides decorators and utilities for handling Gmail API errors,
including automatic retries with exponential backoff.
"""

import time
import logging
import functools
from typing import Type, Tuple, Optional, Callable, Any
from googleapiclient.errors import HttpError
from app.core.exceptions import (
    GmailCleanerError,
    NetworkError,
    AuthError,
    GmailApiError,
    QuotaExceededError,
    ResourceNotFoundError,
)

logger = logging.getLogger(__name__)


def handle_gmail_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to catch and transform Gmail API errors into custom exceptions.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as e:
            error_details = _parse_http_error(e)
            status_code = e.resp.status

            if status_code == 401:
                raise AuthError(
                    "Authentication expired or invalid", details=error_details
                ) from e
            elif status_code == 403:
                # Check for quota errors
                if "quota" in str(error_details).lower():
                    raise QuotaExceededError(
                        "Gmail API quota exceeded", details=error_details
                    ) from e
                raise GmailApiError(
                    "Permission denied", status_code=403, details=error_details
                ) from e
            elif status_code == 404:
                raise ResourceNotFoundError(
                    "Resource not found", details=error_details
                ) from e
            elif status_code == 429:
                raise QuotaExceededError(
                    "Too many requests", details=error_details
                ) from e
            elif status_code >= 500:
                raise GmailApiError(
                    "Gmail service error",
                    status_code=status_code,
                    details=error_details,
                ) from e
            else:
                raise GmailApiError(
                    f"Gmail API error: {status_code}",
                    status_code=status_code,
                    details=error_details,
                ) from e
        except Exception as e:
            if isinstance(e, GmailCleanerError):
                raise
            logger.exception(f"Unexpected error in {func.__name__}")
            raise GmailCleanerError(
                f"Unexpected error: {str(e)}", code="INTERNAL_ERROR"
            ) from e

    return wrapper


def with_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (NetworkError, GmailApiError),
    exclude_exceptions: Tuple[Type[Exception], ...] = (
        AuthError,
        ResourceNotFoundError,
        QuotaExceededError,
    ),
) -> Callable[..., Any]:
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each failure
        exceptions: Tuple of exceptions to retry on
        exclude_exceptions: Tuple of exceptions to NOT retry on (fail immediately)
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if we should stop retrying
                    if isinstance(e, exclude_exceptions):
                        raise

                    # Check if we should retry
                    should_retry = False
                    if isinstance(e, exceptions):
                        should_retry = True
                    elif isinstance(e, HttpError):
                        # Retry on 5xx errors and some 4xx (rate limits)
                        status = e.resp.status
                        if status >= 500 or status == 429:
                            should_retry = True

                    if not should_retry or attempt == max_retries:
                        raise

                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                        f"after error: {str(e)}. Waiting {delay}s..."
                    )
                    time.sleep(delay)
                    delay *= backoff_factor

            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def _parse_http_error(error: HttpError) -> dict:
    """Extract useful details from HttpError."""
    try:
        import json

        if error.content:
            content = json.loads(error.content.decode("utf-8"))
            return content.get("error", {})
    except (ValueError, AttributeError):
        pass
    return {"message": str(error)}
