"""
Standardized API Response Models.

This module provides consistent response formatting for all API endpoints.
It includes standard success/error responses and paginated response support
using Pydantic models for automatic validation and serialization.

Response Types:
- APIResponse: Standard success/error response format
- PaginatedResponse: Response with pagination metadata for list endpoints
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class APIResponse(BaseModel):
    """
    Standard API response format for all endpoints.
    
    Provides consistent structure for both success and error responses
    with optional data payload and automatic timestamp generation.
    
    Attributes:
        success (bool): Indicates if the operation was successful
        message (str): Human-readable description of the result
        data (Any, optional): Response payload (can be any JSON-serializable type)
    
    Example:
        # Success response
        APIResponse.success_response(
            message="User created successfully",
            data={"id": 123, "name": "John Doe"}
        )
        
        # Error response  
        APIResponse.error_response(
            message="User not found",
            data={"user_id": 123}
        )
    """
    
    success: bool = Field(
        description="Indicates whether the operation was successful"
    )
    message: str = Field(
        description="Human-readable description of the operation result"
    )
    data: Optional[Any] = Field(
        default=None,
        description="Optional response payload data"
    )
    
    @classmethod
    def success_response(
        cls,
        message: str = "Operation successful",
        data: Any = None,
    ) -> "APIResponse":
        """
        Create a standardized success response.
        
        Args:
            message (str): Success message to include in response
            data (Any, optional): Data payload to include
            
        Returns:
            APIResponse: Formatted success response
        """
        return cls(
            success=True,
            message=message,
            data=data
        )
    
    @classmethod
    def error_response(
        cls,
        message: str,
        data: Any = None
    ) -> "APIResponse":
        """
        Create a standardized error response.
        
        Args:
            message (str): Error message to include in response
            data (Any, optional): Additional error context data
            
        Returns:
            APIResponse: Formatted error response
        """
        return cls(
            success=False,
            message=message,
            data=data
        )


class PaginatedResponse(BaseModel):
    """
    Paginated API response format for list endpoints.
    
    Provides consistent pagination structure with metadata
    for navigating through large datasets.
    
    Attributes:
        success (bool): Always True for successful paginated responses
        message (str): Description of the paginated data
        data (Any): List of items for current page
        pagination (Dict): Pagination metadata and navigation info
        
    Example:
        PaginatedResponse.create(
            data=[{"id": 1, "name": "Item 1"}],
            total=100,
            page=1,
            per_page=10,
            message="Users retrieved successfully"
        )
    """
    
    success: bool = Field(
        default=True,
        description="Always true for successful paginated responses"
    )
    message: str = Field(
        default="Data retrieved successfully",
        description="Description of the paginated data"
    )
    data: Any = Field(
        description="List of items for the current page"
    )
    pagination: Dict[str, Any] = Field(
        description="Pagination metadata and navigation information"
    )
    
    @classmethod
    def create(
        cls,
        data: Any,
        total: int,
        page: int = 1,
        per_page: int = 10,
        message: str = "Data retrieved successfully"
    ) -> "PaginatedResponse":
        """
        Create a paginated response with calculated metadata.
        
        Automatically calculates pagination metadata including
        total pages, navigation flags, and current position.
        
        Args:
            data (Any): List of items for current page
            total (int): Total number of items across all pages
            page (int): Current page number (1-indexed)
            per_page (int): Number of items per page
            message (str): Response message
            
        Returns:
            PaginatedResponse: Complete paginated response with metadata
            
        Example:
            # Get page 2 of users with 10 items per page
            response = PaginatedResponse.create(
                data=user_list,
                total=156,
                page=2,
                per_page=10
            )
            # pagination.has_next = True (more pages available)
            # pagination.has_prev = True (can go to page 1)
            # pagination.total_pages = 16
        """
        # Calculate total pages (round up division)
        total_pages = (total + per_page - 1) // per_page
        
        return cls(
            message=message,
            data=data,
            pagination={
                "total": total,              # Total items across all pages
                "page": page,                # Current page number
                "per_page": per_page,        # Items per page
                "total_pages": total_pages,  # Total number of pages
                "has_next": page < total_pages,  # More pages available
                "has_prev": page > 1         # Previous pages available
            }
        )


# Export response models for external use
__all__ = ["APIResponse", "PaginatedResponse"]