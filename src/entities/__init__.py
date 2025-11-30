"""
Entities Package.

This package contains SQLAlchemy database models and entity definitions
for the application's domain objects.

Note: This microservice only stores IDs for external entities (companies, 
branches, departments, teams, users) as they are managed by separate microservices.

Modules:
- board: Main board container entity
- board_list: Lists/columns within boards  
- card: Individual task cards within lists
- label: Labels for categorizing cards
- card_comment: Comments on cards
- card_attachment: File attachments on cards
- card_label: Many-to-many association between cards and labels
- enums: Shared enums used across entities
"""

from .board import Board
from .board_list import BoardList
from .card import Card
from .label import Label
from .card_comment import CardComment
from .card_attachment import CardAttachment
from .card_label import CardLabel
from .enums import BoardStatus, BoardVisibility, Priority, CardStatus

__all__ = [
    # Entity classes
    "Board", "BoardList", "Card", "Label", "CardComment", "CardAttachment", "CardLabel",
    
    # Enums
    "BoardStatus", "BoardVisibility", "Priority", "CardStatus"
]