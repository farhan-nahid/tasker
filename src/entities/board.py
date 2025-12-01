from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
import uuid
import re

from ..configs.database import Base
from .enums import BoardStatus, BoardVisibility, Priority


class Board(Base):
    __tablename__ = "boards"

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid8, index=True)
    
    # Core board information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    color = Column(String(7), default="#0079bf")  # Hex color code
    
    # Organizational structure (IDs only - managed by other microservices)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    branch_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    department_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    team_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Ownership and permissions (IDs only - user service manages users)
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    members = Column(ARRAY(UUID(as_uuid=True)), default=list)
    admins = Column(ARRAY(UUID(as_uuid=True)), default=list)
    
    # Board settings
    status = Column(Enum(BoardStatus), default=BoardStatus.ACTIVE, nullable=False, index=True)
    visibility = Column(Enum(BoardVisibility), default=BoardVisibility.TEAM, nullable=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM, nullable=False)
    
    # Features toggles
    enable_comments = Column(Boolean, default=True, nullable=False)
    enable_attachments = Column(Boolean, default=True, nullable=False)
    enable_due_dates = Column(Boolean, default=True, nullable=False)
    enable_labels = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True, index=True)
    
    created_by = Column(UUID(as_uuid=True), nullable=False, index=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_board_company_status', 'company_id', 'status'),
        Index('idx_board_owner_created', 'owner_id', 'created_at'),
    )
    
    @validates('name')
    def validate_name(self, key, name):
        """Validate board name."""
        if not name or len(name.strip()) < 1:
            raise ValueError("Board name cannot be empty")
        if len(name) > 255:
            raise ValueError("Board name cannot exceed 255 characters")
        return name.strip()
    
    @validates('color')
    def validate_color(self, key, color):
        """Validate hex color code."""
        if color and not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValueError("Color must be a valid hex code (e.g., #0079bf)")
        return color or "#0079bf"
    
    @validates('members')
    def validate_members(self, key, members):
        """Validate members array."""
        if members is None:
            return []
        if len(members) > 100:  # Reasonable limit
            raise ValueError("Board cannot have more than 100 members")
        return list(set(members))  # Remove duplicates


# Export Board model
__all__ = ["Board"]