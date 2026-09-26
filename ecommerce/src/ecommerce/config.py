"""Application configuration, read once from the environment at startup.

Every setting has a documented default, so the server starts with no configuration file
present, empty, or partially filled (FR-010). An invalid value fails startup naming the
setting and its accepted values rather than falling back silently (FR-011): a typo that
quietly disabled the API descriptions would present as a working server with no
documentation, which is far harder to diagnose than a refusal to start.

The object is frozen. Settings are read once at startup, so behaviour must not depend on
request order.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(StrEnum):
    """Runtime environment. Accepted values are published in docs/configuration.md."""

    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """The settings this feature reads. See contracts/configuration.md."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    # -- Application identity -------------------------------------------------
    app_name: str = Field(default="Fake E-Commerce Server")
    app_version: str = Field(default="0.1.0")
    app_env: AppEnv = Field(default=AppEnv.DEVELOPMENT)

    # -- API ------------------------------------------------------------------
    api_v1_prefix: str = Field(default="/api/v1")
    api_docs_enabled: bool = Field(default=True)
    api_redoc_enabled: bool = Field(default=True)

    # -- Server ----------------------------------------------------------------
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)

    @field_validator("api_v1_prefix")
    @classmethod
    def _prefix_must_be_a_usable_namespace(cls, value: str) -> str:
        """An empty or conflicting prefix is rejected.

        An empty prefix would place future business routes outside the versioned
        namespace, breaking the contract every client depends on (FR-006, edge case).
        """
        normalised = value.rstrip("/")
        if not normalised or not normalised.startswith("/"):
            raise ValueError(
                f"API_V1_PREFIX must be a non-empty absolute path beginning with '/', got {value!r}. "
                "An empty prefix would place business routes outside the versioned namespace."
            )
        return normalised

    @field_validator("api_docs_enabled", "api_redoc_enabled", mode="before")
    @classmethod
    def _switch_must_be_a_real_boolean(cls, value: object) -> object:
        """A non-boolean switch value is an error, never read as "off".

        Pydantic would otherwise coerce an unrecognised string to ``False`` on some
        inputs, so a typo such as ``API_DOCS_ENABLED=flase`` would silently disable both
        descriptions. The caller reports the setting and its accepted values.
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes", "on"}:
                return True
            if lowered in {"false", "0", "no", "off"}:
                return False
            raise ValueError(
                f"expected a boolean (true/false), got {value!r}. "
                "A value that is not a boolean is never treated as 'off'."
            )
        raise ValueError(f"expected a boolean (true/false), got {value!r}")


def get_settings() -> Settings:
    """Build the settings object. Called once, when the application is created."""
    return Settings()
