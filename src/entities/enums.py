import enum


class Priority(enum.Enum):
    """Priority levels for boards and cards."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class BoardStatus(enum.Enum):
    """Board status options with clear semantics."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DELETED = "deleted"


class BoardVisibility(enum.Enum):
    """Board visibility/privacy settings."""
    PRIVATE = "private"
    TEAM = "team"
    ORGANIZATION = "organization"
    PUBLIC = "public"


class CardStatus(enum.Enum):
    """Card status within a list."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


# Export all enums
__all__ = ["Priority", "BoardStatus", "BoardVisibility", "CardStatus"]