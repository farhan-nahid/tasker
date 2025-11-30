# Trello-like Board System: Complete Model Analysis & Relationships

## 📊 **Complete Entity Models Overview**

### 1. **Board Model** (`boards` table)
**Purpose**: Main container for organizing work projects/workspaces

**Fields**:
```python
# Identity & Core Info
id: UUID                    # Primary key, auto-generated
name: String(255)           # Board name, required, indexed, validated (1-255 chars)
description: Text           # Optional detailed description
color: String(7)            # Hex color code (#0079bf), validated regex

# External References (Microservices)
company_id: UUID            # Required, indexed - Company Service
branch_id: UUID             # Optional, indexed - Organization Service  
department_id: UUID         # Optional, indexed - Organization Service
team_id: UUID               # Optional, indexed - Organization Service
owner_id: UUID              # Required, indexed - User Service

# Access Control
members: ARRAY[UUID]        # Array of user IDs, max 100, duplicates removed
admins: ARRAY[UUID]         # Array of admin user IDs
status: BoardStatus         # ACTIVE, INACTIVE, ARCHIVED, DELETED
visibility: BoardVisibility # PRIVATE, TEAM, ORGANIZATION, PUBLIC
priority: Priority          # LOW, MEDIUM, HIGH, URGENT

# Feature Toggles
enable_comments: Boolean     # Default True
enable_attachments: Boolean  # Default True  
enable_due_dates: Boolean   # Default True
enable_labels: Boolean      # Default True

# Timestamps
created_at: DateTime        # Auto-set, indexed
updated_at: DateTime        # Auto-updated
deleted_at: DateTime        # Soft delete, indexed, nullable
```

**Indexes**:
- `idx_board_company_status` (company_id, status)
- `idx_board_owner_created` (owner_id, created_at)

---

### 2. **BoardList Model** (`board_lists` table)
**Purpose**: Vertical columns within boards (To Do, In Progress, Done)

**Fields**:
```python
# Identity
id: UUID                    # Primary key, auto-generated
board_id: UUID              # Required, indexed - References Board

# Core Info
name: String(255)           # Required, validated (1-255 chars)
color: String(7)            # Hex color (#026aa7), validated
position: Integer           # Required, for ordering, default 0

# Settings
is_archived: Boolean        # Default False
card_limit: Integer         # Optional WIP limit (1-1000)

# Timestamps
created_at: DateTime        # Auto-set
updated_at: DateTime        # Auto-updated
```

**Constraints**:
- `uq_board_list_position`: Unique (board_id, position)

**Indexes**:
- `idx_list_board_position` (board_id, position)

---

### 3. **Card Model** (`cards` table)
**Purpose**: Individual tasks/work items within lists

**Fields**:
```python
# Identity
id: UUID                    # Primary key, auto-generated
list_id: UUID               # Required, indexed - References BoardList

# Core Info
title: String(500)          # Required, indexed, validated (1-500 chars)
description: Text           # Optional detailed description
position: Integer           # Required, for ordering, default 0

# Assignment (External User Service)
assignee_id: UUID           # Optional, indexed - User Service
reporter_id: UUID           # Required, indexed - User Service  
watchers: ARRAY[UUID]       # Array of user IDs watching this card

# Properties
status: CardStatus          # OPEN, IN_PROGRESS, COMPLETED, BLOCKED, CANCELLED
priority: Priority          # LOW, MEDIUM, HIGH, URGENT

# Dates
due_date: DateTime          # Optional, indexed
start_date: DateTime        # Optional
completed_at: DateTime      # Auto-set when status = COMPLETED

# Progress
checklist_items: Integer    # Total checklist items, default 0
checklist_completed: Integer # Completed items, validated ≤ total

# Timestamps
created_at: DateTime        # Auto-set, indexed
updated_at: DateTime        # Auto-updated
archived_at: DateTime       # Soft archive, nullable
```

**Constraints**:
- `uq_card_list_position`: Unique (list_id, position)

**Indexes**:
- `idx_card_assignee_status` (assignee_id, status)
- `idx_card_due_date` (due_date)

**Computed Properties**:
- `is_overdue`: Boolean - True if due_date < now() and status != COMPLETED

---

### 4. **Label Model** (`labels` table)
**Purpose**: Color-coded tags for categorizing cards

**Fields**:
```python
# Identity
id: UUID                    # Primary key, auto-generated
board_id: UUID              # Required, indexed - References Board

# Core Info  
name: String(100)           # Required, validated (1-100 chars)
color: String(7)            # Required, hex color (#61bd4f)
description: String(500)    # Optional

# Timestamps
created_at: DateTime        # Auto-set
```

**Constraints**:
- `uq_board_label_name`: Unique (board_id, name)

---

### 5. **CardComment Model** (`card_comments` table)
**Purpose**: Comments/discussion on cards

**Fields**:
```python
# Identity
id: UUID                    # Primary key, auto-generated
card_id: UUID               # Required, indexed - References Card
author_id: UUID             # Required, indexed - User Service

# Content
content: Text               # Required, validated (1-10000 chars)
is_edited: Boolean          # Default False, tracks edits

# Timestamps  
created_at: DateTime        # Auto-set, indexed
updated_at: DateTime        # Auto-updated
```

**Indexes**:
- `idx_comment_card_created` (card_id, created_at)

---

### 6. **CardAttachment Model** (`card_attachments` table)
**Purpose**: File attachments on cards

**Fields**:
```python
# Identity
id: UUID                    # Primary key, auto-generated
card_id: UUID               # Required, indexed - References Card
uploader_id: UUID           # Required - User Service

# File Info
filename: String(255)       # System filename, validated
original_filename: String(255) # User's original filename
file_path: String(500)      # Storage path
file_size: Integer          # Size in bytes, max 50MB
mime_type: String(100)      # File type

# Timestamps
uploaded_at: DateTime       # Auto-set
```

**Indexes**:
- `idx_attachment_card_uploaded` (card_id, uploaded_at)

---

### 7. **CardLabel Model** (`card_labels` table)
**Purpose**: Many-to-many association between cards and labels

**Fields**:
```python
# Identity
id: UUID                    # Primary key, auto-generated
card_id: UUID               # Required, indexed - References Card
label_id: UUID              # Required, indexed - References Label

# Timestamps
created_at: DateTime        # Auto-set
```

**Constraints**:
- `uq_card_label`: Unique (card_id, label_id)

**Indexes**:
- `idx_card_label_card` (card_id)
- `idx_card_label_label` (label_id)

---

## 🔗 **Entity Relationships & Data Flow**

### **Hierarchical Structure**:
```
Company/Organization (External Service)
├── Board (1:N with Lists)
    ├── BoardList (1:N with Cards)
    │   └── Card (N:M with Labels, 1:N with Comments/Attachments)
    │       ├── CardComment
    │       ├── CardAttachment  
    │       └── CardLabel → Label
    └── Label (N:M with Cards via CardLabel)
```

### **Cross-Service References**:
```
User Service:
├── owner_id → Board
├── members[] → Board
├── assignee_id → Card
├── reporter_id → Card
├── watchers[] → Card
├── author_id → CardComment
└── uploader_id → CardAttachment

Organization Service:
├── company_id → Board
├── branch_id → Board
├── department_id → Board
└── team_id → Board
```

### **Internal Relationships**:
```
Board (1:N) → BoardList → (1:N) Card
Board (1:N) → Label
Card (N:M) → Label (via CardLabel)
Card (1:N) → CardComment
Card (1:N) → CardAttachment
```

---

## 📈 **Business Logic & Computed Fields**

### **Card Progress Tracking**:
- **Completion Percentage**: `(checklist_completed / checklist_items) * 100`
- **Overdue Status**: `due_date < now() AND status != COMPLETED`
- **Time in Status**: `now() - updated_at` when status last changed

### **Board Metrics**:
- **Total Cards**: Count of all cards in board lists
- **Completion Rate**: Percentage of cards with status COMPLETED
- **Overdue Cards**: Count of cards where `is_overdue = true`
- **Active Members**: Distinct users in assignee_id, reporter_id across cards

### **List Metrics**:
- **Card Count**: Number of cards in list
- **WIP Limit Status**: `card_count <= card_limit` (if limit set)
- **Average Card Age**: Average time cards have been in list

---

## 🎯 **Data Validation Rules**

### **Field Validations**:
1. **Names/Titles**: Non-empty, trimmed, length limits
2. **Colors**: Valid hex codes (#RRGGBB)
3. **Arrays**: Duplicate removal, size limits
4. **File Sizes**: 50MB maximum for attachments
5. **Dates**: Future dates for due dates, logical date ordering
6. **Progress**: checklist_completed ≤ checklist_items

### **Business Rules**:
1. **Position Uniqueness**: No two items can have same position in same parent
2. **Member Limits**: Maximum 100 members per board
3. **Label Uniqueness**: Label names must be unique within board
4. **Archive Logic**: Archived items hidden but not deleted
5. **Soft Deletes**: Use deleted_at instead of hard deletes

---

## 🚀 **Performance Considerations**

### **Strategic Indexes**:
1. **Lookup Indexes**: Primary relationships (board_id, list_id, card_id)
2. **Query Indexes**: Frequently filtered fields (status, assignee_id, due_date)
3. **Composite Indexes**: Multi-column queries (company_id + status)
4. **Ordering Indexes**: Position-based queries

### **Optimization Strategies**:
1. **Pagination**: Use cursor-based pagination for large datasets
2. **Eager Loading**: Load related data in single queries
3. **Caching**: Cache frequently accessed board/list data
4. **Archiving**: Separate archived data to improve active query performance

This structure provides a robust foundation for a scalable Trello-like application with proper microservices separation!

# Tasker - Trello-like Board Management System

## Overview
A comprehensive Trello-like board management system built with FastAPI and SQLAlchemy, designed for microservices architecture.

## Entity Models

### 1. Board (Main Container)
```python
{
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Product Development Board",
    "description": "Main board for tracking product development tasks and features",
    "color": "#0079bf",
    "company_id": "550e8400-e29b-41d4-a716-446655440010",
    "branch_id": "550e8400-e29b-41d4-a716-446655440011", 
    "department_id": "550e8400-e29b-41d4-a716-446655440012",
    "team_id": "550e8400-e29b-41d4-a716-446655440013",
    "owner_id": "550e8400-e29b-41d4-a716-446655440020",
    "members": [
        "550e8400-e29b-41d4-a716-446655440021",
        "550e8400-e29b-41d4-a716-446655440022",
        "550e8400-e29b-41d4-a716-446655440023"
    ],
    "admins": [
        "550e8400-e29b-41d4-a716-446655440020",
        "550e8400-e29b-41d4-a716-446655440021"
    ],
    "status": "ACTIVE",
    "visibility": "TEAM",
    "priority": "HIGH",
    "enable_comments": true,
    "enable_attachments": true,
    "enable_due_dates": true,
    "enable_labels": true,
    "created_at": "2024-12-01T10:00:00Z",
    "updated_at": "2024-12-01T15:30:00Z",
    "deleted_at": null
}
```

### 2. BoardList (Columns)
```python
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440100",
        "board_id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "To Do",
        "color": "#026aa7",
        "position": 0,
        "is_archived": false,
        "card_limit": 10,
        "created_at": "2024-12-01T10:05:00Z",
        "updated_at": "2024-12-01T10:05:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440101",
        "board_id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "In Progress",
        "color": "#f2d600",
        "position": 1,
        "is_archived": false,
        "card_limit": 5,
        "created_at": "2024-12-01T10:06:00Z",
        "updated_at": "2024-12-01T10:06:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440102",
        "board_id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Review",
        "color": "#ff9f1a",
        "position": 2,
        "is_archived": false,
        "card_limit": 3,
        "created_at": "2024-12-01T10:07:00Z",
        "updated_at": "2024-12-01T10:07:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440103",
        "board_id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Done",
        "color": "#61bd4f",
        "position": 3,
        "is_archived": false,
        "card_limit": null,
        "created_at": "2024-12-01T10:08:00Z",
        "updated_at": "2024-12-01T10:08:00Z"
    }
]
```

### 3. Labels
```python
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440200",
        "board_id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Bug",
        "color": "#eb5a46",
        "description": "Issues that need to be fixed",
        "created_at": "2024-12-01T10:10:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440201",
        "board_id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Feature",
        "color": "#61bd4f",
        "description": "New functionality to be implemented",
        "created_at": "2024-12-01T10:11:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440202",
        "board_id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Enhancement",
        "color": "#ff9f1a",
        "description": "Improvements to existing features",
        "created_at": "2024-12-01T10:12:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440203",
        "board_id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Urgent",
        "color": "#c377e0",
        "description": "High priority items",
        "created_at": "2024-12-01T10:13:00Z"
    }
]
```

### 4. Cards
```python
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440300",
        "list_id": "550e8400-e29b-41d4-a716-446655440100",
        "title": "Implement user authentication system",
        "description": "Create a secure authentication system with JWT tokens, password hashing, and session management. Include features for login, logout, password reset, and account verification.",
        "position": 0,
        "assignee_id": "550e8400-e29b-41d4-a716-446655440021",
        "reporter_id": "550e8400-e29b-41d4-a716-446655440020",
        "watchers": [
            "550e8400-e29b-41d4-a716-446655440022",
            "550e8400-e29b-41d4-a716-446655440023"
        ],
        "status": "OPEN",
        "priority": "HIGH",
        "due_date": "2024-12-15T18:00:00Z",
        "start_date": "2024-12-02T09:00:00Z",
        "completed_at": null,
        "checklist_items": 5,
        "checklist_completed": 0,
        "created_at": "2024-12-01T10:15:00Z",
        "updated_at": "2024-12-01T14:20:00Z",
        "archived_at": null
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440301",
        "list_id": "550e8400-e29b-41d4-a716-446655440101",
        "title": "Design database schema",
        "description": "Create comprehensive database schema for the board management system including all entities and relationships.",
        "position": 0,
        "assignee_id": "550e8400-e29b-41d4-a716-446655440022",
        "reporter_id": "550e8400-e29b-41d4-a716-446655440020",
        "watchers": [
            "550e8400-e29b-41d4-a716-446655440021"
        ],
        "status": "IN_PROGRESS",
        "priority": "MEDIUM",
        "due_date": "2024-12-10T17:00:00Z",
        "start_date": "2024-12-01T10:00:00Z",
        "completed_at": null,
        "checklist_items": 8,
        "checklist_completed": 3,
        "created_at": "2024-12-01T10:16:00Z",
        "updated_at": "2024-12-01T16:45:00Z",
        "archived_at": null
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440302",
        "list_id": "550e8400-e29b-41d4-a716-446655440102",
        "title": "Fix login page styling",
        "description": "The login page has inconsistent styling and needs to match the design system. Update CSS and ensure responsive design works properly.",
        "position": 0,
        "assignee_id": "550e8400-e29b-41d4-a716-446655440023",
        "reporter_id": "550e8400-e29b-41d4-a716-446655440021",
        "watchers": [
            "550e8400-e29b-41d4-a716-446655440020"
        ],
        "status": "COMPLETED",
        "priority": "LOW",
        "due_date": "2024-12-05T16:00:00Z",
        "start_date": "2024-11-30T14:00:00Z",
        "completed_at": "2024-12-01T11:30:00Z",
        "checklist_items": 3,
        "checklist_completed": 3,
        "created_at": "2024-11-30T14:00:00Z",
        "updated_at": "2024-12-01T11:30:00Z",
        "archived_at": null
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440303",
        "list_id": "550e8400-e29b-41d4-a716-446655440103",
        "title": "Setup CI/CD pipeline",
        "description": "Configure GitHub Actions for automated testing, building, and deployment. Include code quality checks and security scanning.",
        "position": 0,
        "assignee_id": "550e8400-e29b-41d4-a716-446655440021",
        "reporter_id": "550e8400-e29b-41d4-a716-446655440020",
        "watchers": [],
        "status": "COMPLETED",
        "priority": "MEDIUM",
        "due_date": "2024-11-28T17:00:00Z",
        "start_date": "2024-11-25T09:00:00Z",
        "completed_at": "2024-11-28T15:45:00Z",
        "checklist_items": 6,
        "checklist_completed": 6,
        "created_at": "2024-11-25T09:00:00Z",
        "updated_at": "2024-11-28T15:45:00Z",
        "archived_at": null
    }
]
```

### 5. Card Labels (Associations)
```python
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440400",
        "card_id": "550e8400-e29b-41d4-a716-446655440300",
        "label_id": "550e8400-e29b-41d4-a716-446655440201",
        "created_at": "2024-12-01T10:15:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440401",
        "card_id": "550e8400-e29b-41d4-a716-446655440300",
        "label_id": "550e8400-e29b-41d4-a716-446655440203",
        "created_at": "2024-12-01T10:15:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440402",
        "card_id": "550e8400-e29b-41d4-a716-446655440301",
        "label_id": "550e8400-e29b-41d4-a716-446655440201",
        "created_at": "2024-12-01T10:16:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440403",
        "card_id": "550e8400-e29b-41d4-a716-446655440302",
        "label_id": "550e8400-e29b-41d4-a716-446655440200",
        "created_at": "2024-11-30T14:00:00Z"
    }
]
```

### 6. Card Comments
```python
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440500",
        "card_id": "550e8400-e29b-41d4-a716-446655440300",
        "author_id": "550e8400-e29b-41d4-a716-446655440020",
        "content": "Let's start with OAuth integration and JWT token management. We should use bcrypt for password hashing.",
        "is_edited": false,
        "created_at": "2024-12-01T11:00:00Z",
        "updated_at": "2024-12-01T11:00:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440501",
        "card_id": "550e8400-e29b-41d4-a716-446655440300",
        "author_id": "550e8400-e29b-41d4-a716-446655440021",
        "content": "Agreed! I'll also add rate limiting to prevent brute force attacks. Should we include 2FA support?",
        "is_edited": false,
        "created_at": "2024-12-01T11:15:00Z",
        "updated_at": "2024-12-01T11:15:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440502",
        "card_id": "550e8400-e29b-41d4-a716-446655440301",
        "author_id": "550e8400-e29b-41d4-a716-446655440022",
        "content": "I've completed the user and board schemas. Working on the relationships now. The microservices approach is working well.",
        "is_edited": true,
        "created_at": "2024-12-01T14:30:00Z",
        "updated_at": "2024-12-01T16:45:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440503",
        "card_id": "550e8400-e29b-41d4-a716-446655440302",
        "author_id": "550e8400-e29b-41d4-a716-446655440023",
        "content": "Fixed the responsive design issues and updated the color scheme to match the design system. Ready for review!",
        "is_edited": false,
        "created_at": "2024-12-01T11:25:00Z",
        "updated_at": "2024-12-01T11:25:00Z"
    }
]
```

### 7. Card Attachments
```python
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440600",
        "card_id": "550e8400-e29b-41d4-a716-446655440300",
        "uploader_id": "550e8400-e29b-41d4-a716-446655440021",
        "filename": "auth_system_requirements_20241201.pdf",
        "original_filename": "Authentication System Requirements.pdf",
        "file_path": "/uploads/cards/550e8400-e29b-41d4-a716-446655440300/auth_system_requirements_20241201.pdf",
        "file_size": 2048000,
        "mime_type": "application/pdf",
        "uploaded_at": "2024-12-01T12:00:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440601",
        "card_id": "550e8400-e29b-41d4-a716-446655440300",
        "uploader_id": "550e8400-e29b-41d4-a716-446655440020",
        "filename": "security_guidelines_v2.docx",
        "original_filename": "Security Guidelines v2.docx",
        "file_path": "/uploads/cards/550e8400-e29b-41d4-a716-446655440300/security_guidelines_v2.docx",
        "file_size": 1024000,
        "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "uploaded_at": "2024-12-01T13:30:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440602",
        "card_id": "550e8400-e29b-41d4-a716-446655440301",
        "uploader_id": "550e8400-e29b-41d4-a716-446655440022",
        "filename": "database_schema_diagram.png",
        "original_filename": "Database Schema Diagram.png",
        "file_path": "/uploads/cards/550e8400-e29b-41d4-a716-446655440301/database_schema_diagram.png",
        "file_size": 512000,
        "mime_type": "image/png",
        "uploaded_at": "2024-12-01T15:00:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440603",
        "card_id": "550e8400-e29b-41d4-a716-446655440302",
        "uploader_id": "550e8400-e29b-41d4-a716-446655440023",
        "filename": "login_page_mockup.figma",
        "original_filename": "Login Page Mockup.figma",
        "file_path": "/uploads/cards/550e8400-e29b-41d4-a716-446655440302/login_page_mockup.figma",
        "file_size": 256000,
        "mime_type": "application/octet-stream",
        "uploaded_at": "2024-11-30T16:00:00Z"
    }
]
```

## Model Relationships

### Entity Relationship Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    MICROSERVICES ARCHITECTURE                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐     ┌──────────────┐     ┌──────────────┐  │
│  │   Company   │     │   Branch     │     │  Department  │  │
│  │   Service   │     │   Service    │     │   Service    │  │
│  └─────────────┘     └──────────────┘     └──────────────┘  │
│                                                             │
│  ┌─────────────┐     ┌──────────────┐                      │
│  │    Team     │     │     User     │                      │
│  │   Service   │     │   Service    │                      │
│  └─────────────┘     └──────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    BOARD SERVICE (THIS SERVICE)             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐                                           │
│  │    Board    │ 1:N ─────────┬─────────────────────────┐   │
│  │             │              │                         │   │
│  │ - company_id │              ▼                         │   │
│  │ - team_id    │    ┌─────────────┐           ┌─────────▼───┐ │
│  │ - owner_id   │    │ BoardList   │           │    Label   │ │
│  │ - members[]  │    │             │           │            │ │
│  └─────────────┘    │ - board_id   │           │ - board_id │ │
│                      │ - position   │           └────────────┘ │
│                      └─────────────┘                         │
│                              │ 1:N                           │
│                              ▼                               │
│                      ┌─────────────┐                         │
│                      │    Card     │                         │
│                      │             │                         │
│                      │ - list_id    │                        │
│                      │ - assignee_id│                        │
│                      │ - reporter_id│                        │
│                      │ - watchers[] │                        │
│                      └─────────────┘                         │
│                              │                               │
│                ┌─────────────┼─────────────┐                 │
│                │ 1:N         │ 1:N         │ M:N             │
│                ▼             ▼             ▼                 │
│    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│    │CardComment  │   │CardAttachment│   │ CardLabel   │       │
│    │             │   │              │   │             │       │
│    │ - card_id   │   │ - card_id    │   │ - card_id   │       │
│    │ - author_id │   │ - uploader_id│   │ - label_id  │       │
│    └─────────────┘   └──────────────┘   └─────────────┘       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Model Relationships Summary

### 1. **Board** (1:N relationships)
- **Board → BoardList**: One board has many lists
- **Board → Label**: One board has many labels

### 2. **BoardList** (1:N relationship)
- **BoardList → Card**: One list contains many cards

### 3. **Card** (1:N and M:N relationships)
- **Card → CardComment**: One card has many comments
- **Card → CardAttachment**: One card has many attachments
- **Card ↔ Label**: Many-to-many through CardLabel association

### 4. **External References** (ID-only for microservices)
- **Board**: References company_id, branch_id, department_id, team_id, owner_id, members[], admins[]
- **Card**: References assignee_id, reporter_id, watchers[]
- **CardComment**: References author_id
- **CardAttachment**: References uploader_id

## Key Features

- **Microservices Ready**: No foreign key constraints, only ID references
- **Comprehensive Validation**: Field length limits, format validation, business rules
- **Performance Optimized**: Strategic database indexes
- **Flexible Architecture**: Supports team collaboration and organizational hierarchies
- **Rich Card Features**: Comments, attachments, labels, checklists, due dates
- **Audit Trail**: Created/updated timestamps, soft deletes