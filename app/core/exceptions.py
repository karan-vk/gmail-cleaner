"""
Custom Exception Hierarchy for Gmail Cleaner
--------------------------------------------
Defines specific exceptions for different error categories to allow
granular error handling and user feedback.
"""

from typing import Optional, Dict, Any


class GmailCleanerError(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class NetworkError(GmailCleanerError):
    """Raised when network connectivity issues occur."""

    def __init__(
        self,
        message: str = "Network connection failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code="NETWORK_ERROR", details=details)


class AuthError(GmailCleanerError):
    """Raised when authentication fails (expired token, invalid credentials)."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code="AUTH_ERROR", details=details)


class GmailApiError(GmailCleanerError):
    """Raised when Gmail API returns an error (4xx, 5xx)."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        super().__init__(message, code="GMAIL_API_ERROR", details=details)


class QuotaExceededError(GmailApiError):
    """Raised when Gmail API quota is exceeded."""

    def __init__(
        self,
        message: str = "Gmail API quota exceeded",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=429, details=details)
        self.code = "QUOTA_EXCEEDED"


class ResourceNotFoundError(GmailCleanerError):
    """Raised when a requested resource (email, label) is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code="NOT_FOUND", details=details)


class ValidationError(GmailCleanerError):
    """Raised when input validation fails."""

    def __init__(
        self, message: str = "Invalid input", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code="VALIDATION_ERROR", details=details)
