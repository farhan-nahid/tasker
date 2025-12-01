from pydantic import BaseModel, Field
from typing import Dict


class WelcomeData(BaseModel):
    version: str = Field(description="API version")
    status: str = Field(description="Service status")
    documentation: str = Field(description="Swagger UI documentation URL")
    alternative_docs: str = Field(description="ReDoc documentation URL")


class HealthData(BaseModel):
    status: str = Field(description="Health status")
    uptime: str = Field(description="Uptime status")


class StatusData(BaseModel):
    timestamp: str = Field(description="Current timestamp in ISO format")
    environment: str = Field(description="Current environment (development/production)")
    python_version: str = Field(description="Python version information")
    port: int = Field(description="Server port number")
    endpoints: Dict[str, str] = Field(description="Available API endpoints")


class DBCheckData(BaseModel):
    isConnected: bool = Field(description="Database connectivity status")
    durationMs: float | None = Field(default=None, description="Duration of the connectivity check in milliseconds")
    error: str | None = Field(default=None, description="Error message if the connectivity check failed")