"""
Database Schema and Relationships Visualization.

This module provides a visual representation of the entity relationships
and database schema for the Trello-like board system.
"""

def print_entity_relationship_diagram():
    """Print ASCII diagram showing entity relationships."""
    
    print("""
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    TRELLO-LIKE BOARD SYSTEM - ENTITY RELATIONSHIPS              │
└─────────────────────────────────────────────────────────────────────────────────┘

                              EXTERNAL SERVICES
                         ┌─────────────────────────────┐
                         │       USER SERVICE          │
                         │  ┌─────────────────────────┐ │
                         │  │ Users (owner_id,        │ │
                         │  │ assignee_id, members[]) │ │
                         │  └─────────────────────────┘ │
                         └─────────────────────────────┘
                                        │
                                        │ references
                                        ▼
                         ┌─────────────────────────────┐
                         │   ORGANIZATION SERVICE      │
                         │  ┌─────────────────────────┐ │
                         │  │ Companies, Branches,    │ │
                         │  │ Departments, Teams      │ │
                         │  └─────────────────────────┘ │
                         └─────────────────────────────┘
                                        │
                                        │ references
                                        ▼

                              THIS SERVICE (BOARD SERVICE)
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                               ║
    ║  ┌─────────────────┐                                                         ║
    ║  │     BOARD       │ 1:N                                                     ║
    ║  │                 ├──────────┐                                              ║
    ║  │ • id (PK)       │          │                                              ║
    ║  │ • name          │          ▼                                              ║
    ║  │ • description   │    ┌─────────────────┐                                 ║
    ║  │ • company_id    │    │   BOARD_LIST    │ 1:N                             ║
    ║  │ • owner_id      │    │                 ├──────────┐                      ║
    ║  │ • members[]     │    │ • id (PK)       │          │                      ║
    ║  │ • status        │    │ • board_id (FK) │          ▼                      ║
    ║  │ • visibility    │    │ • name          │    ┌─────────────────┐          ║
    ║  └─────────────────┘    │ • position      │    │      CARD       │          ║
    ║           │              │ • card_limit    │    │                 │          ║
    ║           │ 1:N          └─────────────────┘    │ • id (PK)       │          ║
    ║           ▼                                     │ • list_id (FK)  │          ║
    ║  ┌─────────────────┐                           │ • title         │          ║
    ║  │     LABEL       │                           │ • assignee_id   │          ║
    ║  │                 │           ┌───────────────┤ • reporter_id   │          ║
    ║  │ • id (PK)       │           │               │ • status        │          ║
    ║  │ • board_id (FK) │           │               │ • due_date      │          ║
    ║  │ • name          │           │               └─────────────────┘          ║
    ║  │ • color         │           │                        │                    ║
    ║  └─────────────────┘           │                        │ 1:N                ║
    ║           │                     │                        ▼                    ║
    ║           │ N:M                 │               ┌─────────────────┐          ║
    ║           │                     │               │  CARD_COMMENT   │          ║
    ║           ▼                     │               │                 │          ║
    ║  ┌─────────────────┐           │               │ • id (PK)       │          ║
    ║  │   CARD_LABEL    │◄──────────┘               │ • card_id (FK)  │          ║
    ║  │                 │ N:M                       │ • author_id     │          ║
    ║  │ • id (PK)       │                           │ • content       │          ║
    ║  │ • card_id (FK)  │                           └─────────────────┘          ║
    ║  │ • label_id (FK) │                                    │                    ║
    ║  └─────────────────┘                                    │ 1:N                ║
    ║                                                          ▼                    ║
    ║                                                 ┌─────────────────┐          ║
    ║                                                 │ CARD_ATTACHMENT │          ║
    ║                                                 │                 │          ║
    ║                                                 │ • id (PK)       │          ║
    ║                                                 │ • card_id (FK)  │          ║
    ║                                                 │ • uploader_id   │          ║
    ║                                                 │ • filename      │          ║
    ║                                                 │ • file_size     │          ║
    ║                                                 └─────────────────┘          ║
    ║                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝

    RELATIONSHIP LEGEND:
    ═══════════════════
    • 1:N  = One-to-Many relationship
    • N:M  = Many-to-Many relationship  
    • (PK) = Primary Key
    • (FK) = Foreign Key (ID reference in microservices architecture)
    
    KEY DESIGN PRINCIPLES:
    ═════════════════════
    ✓ No actual foreign key constraints (microservices architecture)
    ✓ All cross-service references are ID-only
    ✓ Each entity can be deployed and scaled independently
    ✓ Referential integrity handled at application level
    ✓ Soft deletes and archiving for data preservation
    """)


def print_data_flow_example():
    """Print example showing data flow through the system."""
    
    print("""
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW EXAMPLE - CREATING A CARD                     │
└─────────────────────────────────────────────────────────────────────────────────┘

    1. User creates card in "In Progress" list
       ┌─────────────────┐
       │   USER ACTION   │
       │ Create new card │
       └─────────────────┘
                │
                ▼
    2. System validates and creates card
       ┌─────────────────┐
       │      CARD       │
       │ list_id: xyz    │
       │ title: "Task"   │
       │ assignee_id: abc│
       │ status: open    │
       └─────────────────┘
                │
                ▼
    3. User adds labels to card
       ┌─────────────────┐
       │   CARD_LABEL    │
       │ card_id: xyz    │
       │ label_id: def   │
       └─────────────────┘
                │
                ▼
    4. User adds comment
       ┌─────────────────┐
       │  CARD_COMMENT   │
       │ card_id: xyz    │
       │ author_id: abc  │
       │ content: "..."  │
       └─────────────────┘
                │
                ▼
    5. User uploads attachment
       ┌─────────────────┐
       │ CARD_ATTACHMENT │
       │ card_id: xyz    │
       │ uploader_id: abc│
       │ filename: "..." │
       └─────────────────┘

    RESULT: Full card with all relationships established!
    """)


def print_database_schema():
    """Print detailed database schema for all tables."""
    
    print("""
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            DATABASE SCHEMA DETAILS                              │
└─────────────────────────────────────────────────────────────────────────────────┘

TABLE: boards
═════════════
CREATE TABLE boards (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    color               VARCHAR(7) DEFAULT '#0079bf',
    company_id          UUID NOT NULL,
    branch_id           UUID,
    department_id       UUID,
    team_id             UUID,
    owner_id            UUID NOT NULL,
    members             UUID[],
    admins              UUID[],
    status              board_status_enum DEFAULT 'active',
    visibility          board_visibility_enum DEFAULT 'team',
    priority            priority_enum DEFAULT 'medium',
    enable_comments     BOOLEAN DEFAULT true,
    enable_attachments  BOOLEAN DEFAULT true,
    enable_due_dates    BOOLEAN DEFAULT true,
    enable_labels       BOOLEAN DEFAULT true,
    created_at          TIMESTAMP DEFAULT now(),
    updated_at          TIMESTAMP DEFAULT now(),
    deleted_at          TIMESTAMP,
    
    CONSTRAINT idx_board_company_status INDEX (company_id, status),
    CONSTRAINT idx_board_owner_created INDEX (owner_id, created_at)
);

TABLE: board_lists
══════════════════
CREATE TABLE board_lists (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    board_id        UUID NOT NULL,
    name            VARCHAR(255) NOT NULL,
    color           VARCHAR(7) DEFAULT '#026aa7',
    position        INTEGER NOT NULL DEFAULT 0,
    is_archived     BOOLEAN DEFAULT false,
    card_limit      INTEGER,
    created_at      TIMESTAMP DEFAULT now(),
    updated_at      TIMESTAMP DEFAULT now(),
    
    CONSTRAINT uq_board_list_position UNIQUE (board_id, position),
    CONSTRAINT idx_list_board_position INDEX (board_id, position)
);

TABLE: cards
════════════
CREATE TABLE cards (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    list_id              UUID NOT NULL,
    title                VARCHAR(500) NOT NULL,
    description          TEXT,
    position             INTEGER NOT NULL DEFAULT 0,
    assignee_id          UUID,
    reporter_id          UUID NOT NULL,
    watchers             UUID[],
    status               card_status_enum DEFAULT 'open',
    priority             priority_enum DEFAULT 'medium',
    due_date             TIMESTAMP,
    start_date           TIMESTAMP,
    completed_at         TIMESTAMP,
    checklist_items      INTEGER DEFAULT 0,
    checklist_completed  INTEGER DEFAULT 0,
    created_at           TIMESTAMP DEFAULT now(),
    updated_at           TIMESTAMP DEFAULT now(),
    archived_at          TIMESTAMP,
    
    CONSTRAINT uq_card_list_position UNIQUE (list_id, position),
    CONSTRAINT idx_card_assignee_status INDEX (assignee_id, status),
    CONSTRAINT idx_card_due_date INDEX (due_date)
);

TABLE: labels
═════════════
CREATE TABLE labels (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    board_id    UUID NOT NULL,
    name        VARCHAR(100) NOT NULL,
    color       VARCHAR(7) DEFAULT '#61bd4f',
    description VARCHAR(500),
    created_at  TIMESTAMP DEFAULT now(),
    
    CONSTRAINT uq_board_label_name UNIQUE (board_id, name)
);

TABLE: card_comments
════════════════════
CREATE TABLE card_comments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id     UUID NOT NULL,
    author_id   UUID NOT NULL,
    content     TEXT NOT NULL,
    is_edited   BOOLEAN DEFAULT false,
    created_at  TIMESTAMP DEFAULT now(),
    updated_at  TIMESTAMP DEFAULT now(),
    
    CONSTRAINT idx_comment_card_created INDEX (card_id, created_at)
);

TABLE: card_attachments
═══════════════════════
CREATE TABLE card_attachments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id             UUID NOT NULL,
    uploader_id         UUID NOT NULL,
    filename            VARCHAR(255) NOT NULL,
    original_filename   VARCHAR(255) NOT NULL,
    file_path           VARCHAR(500) NOT NULL,
    file_size           INTEGER NOT NULL,
    mime_type           VARCHAR(100) NOT NULL,
    uploaded_at         TIMESTAMP DEFAULT now(),
    
    CONSTRAINT idx_attachment_card_uploaded INDEX (card_id, uploaded_at)
);

TABLE: card_labels
══════════════════
CREATE TABLE card_labels (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id     UUID NOT NULL,
    label_id    UUID NOT NULL,
    created_at  TIMESTAMP DEFAULT now(),
    
    CONSTRAINT uq_card_label UNIQUE (card_id, label_id),
    CONSTRAINT idx_card_label_card INDEX (card_id),
    CONSTRAINT idx_card_label_label INDEX (label_id)
);

ENUMS:
══════
CREATE TYPE board_status_enum AS ENUM ('active', 'inactive', 'archived', 'deleted');
CREATE TYPE board_visibility_enum AS ENUM ('private', 'team', 'organization', 'public');
CREATE TYPE card_status_enum AS ENUM ('open', 'in_progress', 'completed', 'blocked', 'cancelled');
CREATE TYPE priority_enum AS ENUM ('low', 'medium', 'high', 'urgent');
    """)


def main():
    """Display all relationship diagrams and schema information."""
    print_entity_relationship_diagram()
    print("\n\n")
    print_data_flow_example()
    print("\n\n")
    print_database_schema()


if __name__ == "__main__":
    main()