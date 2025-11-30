"""
Schemas Package.

This package contains Pydantic models and response schemas used
for data validation, serialization, and API documentation.

- responses: Standard API response models (APIResponse, PaginatedResponse)
- Additional schema files can be added here for specific domains
"""

from .responses import APIResponse, PaginatedResponse

__all__ = [
    "APIResponse",
    "PaginatedResponse"
]