from typing import Any, Dict, Optional, Union
from pydantic import BaseModel
from datetime import datetime


class APIResponse(BaseModel):
    """Standard API response format."""
    
    success: bool
    message: str
    data: Optional[Any] = None
    
    @classmethod
    def success_response(
        cls,
        message: str = "Operation successful",
        data: Any = None,
    ) -> "APIResponse":
        """Create a success response."""
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
        """Create an error response."""
        return cls(
            success=False,
            message=message,
            data=data
        )


class PaginatedResponse(BaseModel):
    """Paginated API response format."""
    
    success: bool = True
    message: str = "Data retrieved successfully"
    data: Any
    pagination: Dict[str, Any]
    
    @classmethod
    def create(
        cls,
        data: Any,
        total: int,
        page: int = 1,
        per_page: int = 10,
        message: str = "Data retrieved successfully"
    ) -> "PaginatedResponse":
        """Create a paginated response."""
        total_pages = (total + per_page - 1) // per_page
        
        return cls(
            message=message,
            data=data,
            pagination={
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        )