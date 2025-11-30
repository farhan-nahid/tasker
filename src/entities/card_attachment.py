from sqlalchemy import Column, String, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
import uuid

from ..configs.database import Base


class CardAttachment(Base):
    __tablename__ = "card_attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Reference to Card service
    uploader_id = Column(UUID(as_uuid=True), nullable=False)  # Reference to User service
    
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    mime_type = Column(String(100), nullable=False)
    
    uploaded_at = Column(DateTime, default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_attachment_card_uploaded', 'card_id', 'uploaded_at'),
    )
    
    @validates('file_size')
    def validate_file_size(self, key, size):
        """Validate file size (max 50MB)."""
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if size > max_size:
            raise ValueError(f"File size cannot exceed {max_size // (1024 * 1024)}MB")
        return size
    
    @validates('filename', 'original_filename')
    def validate_filename(self, key, filename):
        """Validate filename."""
        if not filename or len(filename.strip()) < 1:
            raise ValueError("Filename cannot be empty")
        if len(filename) > 255:
            raise ValueError("Filename cannot exceed 255 characters")
        return filename.strip()


# Export CardAttachment model
__all__ = ["CardAttachment"]