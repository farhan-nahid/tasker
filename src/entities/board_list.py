from sqlalchemy import Column, String, Boolean, DateTime, Integer, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
import uuid
import re

from ..configs.database import Base


class BoardList(Base):
    __tablename__ = "board_lists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    board_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Reference to Board service
    
    name = Column(String(255), nullable=False)
    color = Column(String(7), default="#026aa7")
    position = Column(Integer, nullable=False, default=0)
    
    # List settings
    is_archived = Column(Boolean, default=False, nullable=False)
    card_limit = Column(Integer, nullable=True)  # WIP limit
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('board_id', 'position', name='uq_board_list_position'),
        Index('idx_list_board_position', 'board_id', 'position'),
    )
    
    @validates('name')
    def validate_name(self, key, name):
        """Validate list name."""
        if not name or len(name.strip()) < 1:
            raise ValueError("List name cannot be empty")
        if len(name) > 255:
            raise ValueError("List name cannot exceed 255 characters")
        return name.strip()
    
    @validates('color')
    def validate_color(self, key, color):
        """Validate hex color code."""
        if color and not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValueError("Color must be a valid hex code (e.g., #026aa7)")
        return color or "#026aa7"
    
    @validates('card_limit')
    def validate_card_limit(self, key, limit):
        """Validate WIP limit."""
        if limit is not None and (limit < 1 or limit > 1000):
            raise ValueError("Card limit must be between 1 and 1000")
        return limit


# Export BoardList model
__all__ = ["BoardList"]