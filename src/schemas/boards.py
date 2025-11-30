"""
Pydantic schemas for Board-related entities.

This module provides comprehensive validation schemas for the Trello-like board system,
including request/response models and validation rules.
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from uuid import UUID
import re

from ..entities.enums import BoardStatus, BoardVisibility, Priority, CardStatus


# Base schemas for common fields
class TimestampMixin(BaseModel):
    """Common timestamp fields."""
    created_at: datetime
    updated_at: datetime


class UUIDMixin(BaseModel):
    """Common UUID id field."""
    id: UUID


# Board schemas
class BoardBase(BaseModel):
    """Base board fields for creation and updates."""
    name: str = Field(..., min_length=1, max_length=255, description="Board name")
    description: Optional[str] = Field(None, max_length=5000, description="Board description")
    color: Optional[str] = Field("#0079bf", pattern=r'^#[0-9A-Fa-f]{6}$', description="Hex color code")
    visibility: BoardVisibility = Field(default=BoardVisibility.TEAM, description="Board visibility")
    priority: Priority = Field(default=Priority.MEDIUM, description="Board priority")
    
    # Feature toggles
    enable_comments: bool = Field(default=True, description="Enable comments on cards")
    enable_attachments: bool = Field(default=True, description="Enable file attachments")
    enable_due_dates: bool = Field(default=True, description="Enable due dates on cards")
    enable_labels: bool = Field(default=True, description="Enable labels")

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Board name cannot be empty')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if v and len(v.strip()) > 5000:
            raise ValueError('Description cannot exceed 5000 characters')
        return v.strip() if v else None


class BoardCreate(BoardBase):
    """Schema for creating a new board."""
    company_id: UUID = Field(..., description="Company ID")
    branch_id: Optional[UUID] = Field(None, description="Branch ID")
    department_id: Optional[UUID] = Field(None, description="Department ID")
    team_id: Optional[UUID] = Field(None, description="Team ID")
    members: Optional[List[UUID]] = Field(default_factory=list, description="Initial members")
    admins: Optional[List[UUID]] = Field(default_factory=list, description="Board admins")

    @validator('members', 'admins')
    def validate_member_lists(cls, v):
        if v and len(v) > 100:
            raise ValueError('Cannot have more than 100 members/admins')
        return list(set(v)) if v else []


class BoardUpdate(BaseModel):
    """Schema for updating a board."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    visibility: Optional[BoardVisibility] = None
    priority: Optional[Priority] = None
    status: Optional[BoardStatus] = None
    
    enable_comments: Optional[bool] = None
    enable_attachments: Optional[bool] = None
    enable_due_dates: Optional[bool] = None
    enable_labels: Optional[bool] = None


class BoardResponse(BoardBase, UUIDMixin, TimestampMixin):
    """Complete board response schema."""
    company_id: UUID
    branch_id: Optional[UUID]
    department_id: Optional[UUID]
    team_id: Optional[UUID]
    owner_id: UUID
    members: List[UUID]
    admins: List[UUID]
    status: BoardStatus
    deleted_at: Optional[datetime]
    
    # Computed fields
    member_count: Optional[int] = Field(None, description="Total number of members")
    list_count: Optional[int] = Field(None, description="Number of lists in board")
    card_count: Optional[int] = Field(None, description="Total number of cards")

    class Config:
        from_attributes = True


# BoardList schemas
class BoardListBase(BaseModel):
    """Base list fields."""
    name: str = Field(..., min_length=1, max_length=255, description="List name")
    color: Optional[str] = Field("#026aa7", pattern=r'^#[0-9A-Fa-f]{6}$')
    card_limit: Optional[int] = Field(None, ge=1, le=1000, description="WIP limit")

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('List name cannot be empty')
        return v.strip()


class BoardListCreate(BoardListBase):
    """Schema for creating a new list."""
    board_id: UUID = Field(..., description="Parent board ID")
    position: Optional[int] = Field(0, ge=0, description="List position")


class BoardListUpdate(BaseModel):
    """Schema for updating a list."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    position: Optional[int] = Field(None, ge=0)
    card_limit: Optional[int] = Field(None, ge=1, le=1000)
    is_archived: Optional[bool] = None


class BoardListResponse(BoardListBase, UUIDMixin, TimestampMixin):
    """Complete list response schema."""
    board_id: UUID
    position: int
    is_archived: bool
    card_count: Optional[int] = Field(None, description="Number of cards in list")

    class Config:
        from_attributes = True


# Card schemas
class CardBase(BaseModel):
    """Base card fields."""
    title: str = Field(..., min_length=1, max_length=500, description="Card title")
    description: Optional[str] = Field(None, max_length=10000, description="Card description")
    due_date: Optional[datetime] = Field(None, description="Card due date")
    start_date: Optional[datetime] = Field(None, description="Card start date")
    priority: Priority = Field(default=Priority.MEDIUM, description="Card priority")

    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Card title cannot be empty')
        return v.strip()

    @validator('due_date', 'start_date')
    def validate_dates(cls, v):
        if v and v < datetime.now():
            raise ValueError('Dates cannot be in the past')
        return v


class CardCreate(CardBase):
    """Schema for creating a new card."""
    list_id: UUID = Field(..., description="Parent list ID")
    assignee_id: Optional[UUID] = Field(None, description="Assigned user ID")
    position: Optional[int] = Field(0, ge=0, description="Card position in list")
    label_ids: Optional[List[UUID]] = Field(default_factory=list, description="Label IDs")
    watchers: Optional[List[UUID]] = Field(default_factory=list, description="Watcher user IDs")

    @validator('label_ids', 'watchers')
    def validate_lists(cls, v):
        return list(set(v)) if v else []


class CardUpdate(BaseModel):
    """Schema for updating a card."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=10000)
    list_id: Optional[UUID] = Field(None, description="Move to different list")
    assignee_id: Optional[UUID] = None
    position: Optional[int] = Field(None, ge=0)
    status: Optional[CardStatus] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class CardResponse(CardBase, UUIDMixin, TimestampMixin):
    """Complete card response schema."""
    list_id: UUID
    assignee_id: Optional[UUID]
    reporter_id: UUID
    watchers: List[UUID]
    status: CardStatus
    position: int
    checklist_items: int
    checklist_completed: int
    completed_at: Optional[datetime]
    archived_at: Optional[datetime]
    
    # Computed fields
    is_overdue: Optional[bool] = Field(None, description="Whether card is overdue")
    completion_percentage: Optional[float] = Field(None, description="Checklist completion %")
    comment_count: Optional[int] = Field(None, description="Number of comments")
    attachment_count: Optional[int] = Field(None, description="Number of attachments")

    class Config:
        from_attributes = True


# Label schemas
class LabelBase(BaseModel):
    """Base label fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Label name")
    color: str = Field("#61bd4f", pattern=r'^#[0-9A-Fa-f]{6}$', description="Label color")
    description: Optional[str] = Field(None, max_length=500, description="Label description")

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Label name cannot be empty')
        return v.strip()


class LabelCreate(LabelBase):
    """Schema for creating a new label."""
    board_id: UUID = Field(..., description="Parent board ID")


class LabelUpdate(BaseModel):
    """Schema for updating a label."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    description: Optional[str] = Field(None, max_length=500)


class LabelResponse(LabelBase, UUIDMixin):
    """Complete label response schema."""
    board_id: UUID
    created_at: datetime
    card_count: Optional[int] = Field(None, description="Number of cards with this label")

    class Config:
        from_attributes = True


# Comment schemas
class CommentBase(BaseModel):
    """Base comment fields."""
    content: str = Field(..., min_length=1, max_length=10000, description="Comment content")

    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Comment content cannot be empty')
        return v.strip()


class CommentCreate(CommentBase):
    """Schema for creating a comment."""
    card_id: UUID = Field(..., description="Parent card ID")


class CommentUpdate(BaseModel):
    """Schema for updating a comment."""
    content: str = Field(..., min_length=1, max_length=10000)


class CommentResponse(CommentBase, UUIDMixin, TimestampMixin):
    """Complete comment response schema."""
    card_id: UUID
    author_id: UUID
    is_edited: bool

    class Config:
        from_attributes = True


# Attachment schemas
class AttachmentResponse(UUIDMixin):
    """Attachment response schema."""
    card_id: UUID
    uploader_id: UUID
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    uploaded_at: datetime
    
    # Computed fields
    file_size_mb: Optional[float] = Field(None, description="File size in MB")

    class Config:
        from_attributes = True


# Search and filter schemas
class BoardFilter(BaseModel):
    """Board filtering options."""
    company_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    status: Optional[BoardStatus] = None
    visibility: Optional[BoardVisibility] = None
    owner_id: Optional[UUID] = None
    member_id: Optional[UUID] = None
    search: Optional[str] = Field(None, description="Search in name/description")


class CardFilter(BaseModel):
    """Card filtering options."""
    list_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None
    status: Optional[CardStatus] = None
    priority: Optional[Priority] = None
    has_due_date: Optional[bool] = None
    is_overdue: Optional[bool] = None
    label_ids: Optional[List[UUID]] = None
    search: Optional[str] = Field(None, description="Search in title/description")


# Bulk operation schemas
class BulkCardMove(BaseModel):
    """Schema for moving multiple cards."""
    card_ids: List[UUID] = Field(..., min_items=1, max_items=50)
    target_list_id: UUID
    insert_position: Optional[int] = Field(0, ge=0)


class BulkCardUpdate(BaseModel):
    """Schema for bulk updating cards."""
    card_ids: List[UUID] = Field(..., min_items=1, max_items=50)
    assignee_id: Optional[UUID] = None
    status: Optional[CardStatus] = None
    priority: Optional[Priority] = None
    add_label_ids: Optional[List[UUID]] = Field(default_factory=list)
    remove_label_ids: Optional[List[UUID]] = Field(default_factory=list)


# Export all schemas
__all__ = [
    # Board
    "BoardBase", "BoardCreate", "BoardUpdate", "BoardResponse", "BoardFilter",
    # List
    "BoardListBase", "BoardListCreate", "BoardListUpdate", "BoardListResponse",
    # Card
    "CardBase", "CardCreate", "CardUpdate", "CardResponse", "CardFilter",
    # Label
    "LabelBase", "LabelCreate", "LabelUpdate", "LabelResponse",
    # Comment
    "CommentBase", "CommentCreate", "CommentUpdate", "CommentResponse",
    # Attachment
    "AttachmentResponse",
    # Bulk operations
    "BulkCardMove", "BulkCardUpdate"
]