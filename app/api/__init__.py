"""API routes module."""

from .status import router as status_router
from .actions import router as actions_router
from .setup import router as setup_router

__all__ = ["status_router", "actions_router", "setup_router"]
