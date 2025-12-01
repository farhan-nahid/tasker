from sqlalchemy import Column, String, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
import uuid
import re

from ..configs.database import Base


class Label(Base):
    __tablename__ = "labels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    board_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Reference to Board service
    
    name = Column(String(100), nullable=False)
    color = Column(String(7), nullable=False, default="#61bd4f")
    description = Column(String(500))
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True, index=True)
    
    created_by = Column(UUID(as_uuid=True), nullable=False, index=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    __table_args__ = (
        UniqueConstraint('board_id', 'name', name='uq_board_label_name'),
    )
    
    @validates('name')
    def validate_name(self, key, name):
        """Validate label name."""
        if not name or len(name.strip()) < 1:
            raise ValueError("Label name cannot be empty")
        if len(name) > 100:
            raise ValueError("Label name cannot exceed 100 characters")
        return name.strip()
    
    @validates('color')
    def validate_color(self, key, color):
        """Validate hex color code."""
        if color and not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValueError("Color must be a valid hex code (e.g., #61bd4f)")
        return color or "#61bd4f"


# Export Label model
__all__ = ["Label"]