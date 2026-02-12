"""API routes module."""

from .status import router as status_router
from .actions import router as actions_router
from .setup import router as setup_router

__all__ = ["actions_router", "setup_router", "status_router"]
