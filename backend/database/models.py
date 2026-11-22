from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Integer,
    Float,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    JSON
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from backend.database.connection import Base


# ==========================================
# SUBJECTS TABLE
# ==========================================

class Subject(Base):

    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    documents = relationship(
        "Document",
        back_populates="subject"
    )


# ==========================================
# DOCUMENTS TABLE
# ==========================================

class Document(Base):

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    stored_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    file_path: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    file_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    file_hash: Mapped[str | None] = mapped_column(
        String(64),
        unique=True,
        nullable=True
    )

    extracted_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending"
    )

    subject_id: Mapped[int | None] = mapped_column(
        ForeignKey("subjects.id"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    subject = relationship(
        "Subject",
        back_populates="documents"
    )

    classifications = relationship(
        "Classification",
        back_populates="document",
        cascade="all, delete-orphan"
    )

    processing_history = relationship(
        "ProcessingHistory",
        back_populates="document"
    )


# ==========================================
# CLASSIFICATIONS TABLE
# ==========================================

class Classification(Base):

    __tablename__ = "classifications"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False
    )

    subject_id: Mapped[int | None] = mapped_column(
        ForeignKey("subjects.id"),
        nullable=True
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    model_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    document = relationship(
        "Document",
        back_populates="classifications"
    )


# ==========================================
# FOLDERS TABLE
# ==========================================

class Folder(Base):

    __tablename__ = "folders"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    path: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False
    )

    folder_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


# ==========================================
# PROCESSING HISTORY TABLE
# ==========================================

class ProcessingHistory(Base):

    __tablename__ = "processing_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    document = relationship(
        "Document",
        back_populates="processing_history"
    )


# ==========================================
# ACTIVITY LOGS TABLE
# ==========================================

class ActivityLog(Base):

    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    level: Mapped[str] = mapped_column(
        String(30),
        default="INFO"
    )

    action: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    details: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )