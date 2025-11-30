"""
Schemas Package.

This package contains Pydantic models and response schemas used
for data validation, serialization, and API documentation.

Modules:
- responses: Standard API response models (APIResponse, PaginatedResponse)
- boards: Comprehensive Trello-like board system schemas
"""

from .responses import APIResponse, PaginatedResponse
from .boards import (
    # Board schemas
    BoardBase, BoardCreate, BoardUpdate, BoardResponse, BoardFilter,
    # List schemas
    BoardListBase, BoardListCreate, BoardListUpdate, BoardListResponse,
    # Card schemas
    CardBase, CardCreate, CardUpdate, CardResponse, CardFilter,
    # Label schemas
    LabelBase, LabelCreate, LabelUpdate, LabelResponse,
    # Comment schemas
    CommentBase, CommentCreate, CommentUpdate, CommentResponse,
    # Attachment schemas
    AttachmentResponse,
    # Bulk operation schemas
    BulkCardMove, BulkCardUpdate
)

__all__ = [
    # Core response schemas
    "APIResponse",
    "PaginatedResponse",
    
    # Board schemas
    "BoardBase", "BoardCreate", "BoardUpdate", "BoardResponse", "BoardFilter",
    
    # List schemas
    "BoardListBase", "BoardListCreate", "BoardListUpdate", "BoardListResponse",
    
    # Card schemas
    "CardBase", "CardCreate", "CardUpdate", "CardResponse", "CardFilter",
    
    # Label schemas
    "LabelBase", "LabelCreate", "LabelUpdate", "LabelResponse",
    
    # Comment schemas
    "CommentBase", "CommentCreate", "CommentUpdate", "CommentResponse",
    
    # Attachment schemas
    "AttachmentResponse",
    
    # Bulk operation schemas
    "BulkCardMove", "BulkCardUpdate"
]