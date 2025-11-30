from typing import Any, Dict, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool = Field(
        description="Indicates whether the operation was successful"
    )
    message: str = Field(
        description="Human-readable description of the operation result"
    )
    data: Optional[T] = Field(
        default=None,
        description="Optional response payload data"
    )
    
    @classmethod
    def success_response(
        cls,
        message: str = "Operation successful",
        data: Any = None,
    ) -> "APIResponse":
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
        return cls(
            success=False,
            message=message,
            data=data
        )


class PaginatedResponse(BaseModel):
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