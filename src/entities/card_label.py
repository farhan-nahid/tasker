from sqlalchemy import Column, DateTime, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from ..configs.database import Base


class CardLabel(Base):
    __tablename__ = "card_labels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Reference to Card service
    label_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Reference to Label service
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('card_id', 'label_id', name='uq_card_label'),
        Index('idx_card_label_card', 'card_id'),
        Index('idx_card_label_label', 'label_id'),
    )


# Export CardLabel model
__all__ = ["CardLabel"]