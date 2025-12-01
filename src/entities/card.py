from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum, Text, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from ..configs.database import Base
from .enums import CardStatus, Priority


class Card(Base):
    __tablename__ = "cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    list_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Reference to BoardList service
    
    # Core card information
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    position = Column(Integer, nullable=False, default=0)
    
    # Assignment and ownership (IDs only - user service manages users)
    assignee_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    reporter_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    watchers = Column(ARRAY(UUID(as_uuid=True)), default=list)
    
    # Card properties
    status = Column(Enum(CardStatus), default=CardStatus.OPEN, nullable=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM, nullable=False)
    
    # Dates
    due_date = Column(DateTime, nullable=True, index=True)
    start_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Progress tracking
    checklist_items = Column(Integer, default=0, nullable=False)
    checklist_completed = Column(Integer, default=0, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    archived_at = Column(DateTime, nullable=True, index=True)
    deleted_at = Column(DateTime, nullable=True, index=True)
    
    created_by = Column(UUID(as_uuid=True), nullable=False, index=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Indexes
    __table_args__ = (
        UniqueConstraint('list_id', 'position', name='uq_card_list_position'),
        Index('idx_card_assignee_status', 'assignee_id', 'status'),
        Index('idx_card_due_date', 'due_date'),
    )
    
    @validates('title')
    def validate_title(self, key, title):
        """Validate card title."""
        if not title or len(title.strip()) < 1:
            raise ValueError("Card title cannot be empty")
        if len(title) > 500:
            raise ValueError("Card title cannot exceed 500 characters")
        return title.strip()
    
    @validates('checklist_completed')
    def validate_checklist_progress(self, key, completed):
        """Validate checklist progress."""
        if completed < 0:
            raise ValueError("Checklist completed cannot be negative")
        if hasattr(self, 'checklist_items') and completed > self.checklist_items:
            raise ValueError("Completed items cannot exceed total items")
        return completed

    @property
    def is_overdue(self) -> bool:
        """Check if card is overdue."""
        return (
            self.due_date is not None 
            and self.due_date < datetime.utcnow() 
            and self.status != CardStatus.COMPLETED
        )


# Export Card model
__all__ = ["Card"]