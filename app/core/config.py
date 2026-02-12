"""
Application Configuration
-------------------------
Central configuration and settings for the application.
"""

import os
import platformdirs
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server
    app_name: str = "Gmail Cleaner"
    app_version: str = "1.0.0"
    debug: bool = False
    port: int = 8766
    oauth_port: int = 8767
    oauth_external_port: int | None = Field(
        default=None,
        description="External port for OAuth redirect URI (when different from oauth_port, e.g., Docker port mapping)",
    )

    # Auth
    web_auth: bool = Field(
        default=False,
        description="Enable web-based authentication mode",
    )
    oauth_host: str = Field(
        default="localhost",
        description="Custom host for OAuth redirect (e.g., your domain or IP)",
    )

    @field_validator("web_auth", mode="before")
    @classmethod
    def validate_web_auth(cls, v) -> bool:
        """Convert string environment variable to boolean (case-insensitive)."""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            normalized = v.lower().strip()
            return normalized in ("true", "1", "yes", "on")
        return bool(v)

    credentials_file: str = "credentials.json"
    token_file: str = "token.json"
    data_dir: str = ""

    def __init__(self, **kwargs):
        """Initialize settings and auto-detect data directory for token persistence."""
        super().__init__(**kwargs)

        # 1. Determine Data Directory
        # Check for Docker environment first
        if os.path.exists("/app/data") and os.path.isdir("/app/data"):
            self.data_dir = "/app/data"
        else:
            # Local environment - use platform-specific user data dir
            self.data_dir = platformdirs.user_data_dir(
                "gmail-cleaner", "Gururagavendra"
            )

        # 2. Ensure directory exists
        try:
            os.makedirs(self.data_dir, exist_ok=True)
        except OSError:
            # Fallback to current directory if we can't create the data dir
            # This might happen in some restricted environments
            self.data_dir = os.getcwd()

        # 3. Resolve file paths
        # If the file paths are just filenames (default), join with data_dir
        if not os.path.isabs(self.credentials_file):
            self.credentials_file = os.path.join(self.data_dir, self.credentials_file)

        if not os.path.isabs(self.token_file):
            self.token_file = os.path.join(self.data_dir, self.token_file)

    # Gmail API
    scopes: list[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()
