"""
Setup API Routes
----------------
Endpoints for initial application setup (uploading credentials).
"""

import json
import logging
import os

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core import settings

router = APIRouter(prefix="/api", tags=["Setup"])
logger = logging.getLogger(__name__)


@router.post("/setup")
async def setup_credentials(file: UploadFile = File(...)):
    """Upload credentials.json file."""
    # Check if credentials already exist
    if os.path.exists(settings.credentials_file):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Credentials file already exists. Please delete it manually to upload a new one.",
        )

    try:
        content = await file.read()

        # Validate JSON structure
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON file",
            )

        # Validate content (must be Google OAuth credentials)
        if "installed" not in data and "web" not in data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid credentials file. Must contain 'installed' or 'web' client configuration.",
            )

        # Ensure directory exists
        os.makedirs(
            os.path.dirname(os.path.abspath(settings.credentials_file)), exist_ok=True
        )

        # Save to settings.credentials_file
        with open(settings.credentials_file, "wb") as f:
            f.write(content)

        logger.info(f"Credentials uploaded successfully to {settings.credentials_file}")
        return {
            "message": "Credentials uploaded successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error uploading credentials")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload credentials. Please check server logs.",
        ) from e
