from sqlalchemy import Column, String, Boolean, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
import uuid

from ..configs.database import Base


class CardComment(Base):
    __tablename__ = "card_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Reference to Card service
    author_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Reference to User service
    
    content = Column(Text, nullable=False)
    is_edited = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_comment_card_created', 'card_id', 'created_at'),
    )
    
    @validates('content')
    def validate_content(self, key, content):
        """Validate comment content."""
        if not content or len(content.strip()) < 1:
            raise ValueError("Comment content cannot be empty")
        if len(content) > 10000:
            raise ValueError("Comment cannot exceed 10,000 characters")
        return content.strip()


# Export CardComment model
__all__ = ["CardComment"]