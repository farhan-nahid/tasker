from pydantic import BaseModel, Field
from typing import Dict


class WelcomeData(BaseModel):
    """
    Data model for welcome endpoint response.
    
    Contains basic API information and documentation links.
    """
    version: str = Field(description="API version")
    status: str = Field(description="Service status")
    documentation: str = Field(description="Swagger UI documentation URL")
    alternative_docs: str = Field(description="ReDoc documentation URL")


class HealthData(BaseModel):
    """
    Data model for health check endpoint response.
    
    Contains service health and uptime information.
    """
    status: str = Field(description="Health status")
    uptime: str = Field(description="Uptime status")


class StatusData(BaseModel):
    """
    Data model for detailed status endpoint response.
    
    Contains comprehensive system information including
    environment details, version info, and endpoints.
    """
    timestamp: str = Field(description="Current timestamp in ISO format")
    environment: str = Field(description="Current environment (development/production)")
    python_version: str = Field(description="Python version information")
    port: int = Field(description="Server port number")
    endpoints: Dict[str, str] = Field(description="Available API endpoints")


# Export all models
__all__ = [
    "WelcomeData",
    "HealthData", 
    "StatusData"
]