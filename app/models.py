from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class GmailAccount(Base):
    __tablename__ = "gmail_account"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email_address: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    account_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    processed_emails: Mapped[list["ProcessedEmail"]] = relationship(back_populates="account")


class EmailCategory(Base):
    __tablename__ = "email_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    label_name: Mapped[str] = mapped_column(String(150), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    processed_emails: Mapped[list["ProcessedEmail"]] = relationship(back_populates="category")


class ProcessedEmail(Base):
    __tablename__ = "processed_email"
    __table_args__ = (
        UniqueConstraint("gmail_message_id", "account_id", name="uq_gmail_message_account"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    gmail_message_id: Mapped[str] = mapped_column(String(255), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("gmail_account.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("email_category.id"), nullable=False)
    sender_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sender_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)
    saved_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(50), default="saved")
    thread_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    account: Mapped[GmailAccount] = relationship(back_populates="processed_emails")
    category: Mapped[EmailCategory] = relationship(back_populates="processed_emails")


class SyncLog(Base):
    __tablename__ = "sync_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("gmail_account.id"), nullable=True)
    run_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    total_processed: Mapped[int] = mapped_column(Integer, default=0)
    total_saved: Mapped[int] = mapped_column(Integer, default=0)
    total_ignored: Mapped[int] = mapped_column(Integer, default=0)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
