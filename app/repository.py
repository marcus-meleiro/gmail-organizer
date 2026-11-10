from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EmailCategory, GmailAccount, ProcessedEmail, SyncLog


class Repository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_account(self, account_name: str, email_address: str, account_type: str) -> GmailAccount:
        account = self.db.execute(
            select(GmailAccount).where(GmailAccount.email_address == email_address)
        ).scalar_one_or_none()

        if account is None:
            account = GmailAccount(
                account_name=account_name,
                email_address=email_address,
                account_type=account_type,
            )
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)

        return account

    def get_category_by_name(self, category_name: str) -> EmailCategory | None:
        return self.db.execute(
            select(EmailCategory).where(EmailCategory.category_name == category_name)
        ).scalar_one_or_none()

    def save_processed_email(
        self,
        account_id: int,
        category_id: int,
        gmail_message_id: str,
        sender_email: str | None,
        sender_name: str | None,
        subject: str | None,
        snippet: str | None,
        received_at: datetime | None,
        thread_id: str | None,
    ) -> ProcessedEmail:
        existing = self.db.execute(
            select(ProcessedEmail).where(
                ProcessedEmail.gmail_message_id == gmail_message_id,
                ProcessedEmail.account_id == account_id,
            )
        ).scalar_one_or_none()

        if existing:
            return existing

        email = ProcessedEmail(
            account_id=account_id,
            category_id=category_id,
            gmail_message_id=gmail_message_id,
            sender_email=sender_email,
            sender_name=sender_name,
            subject=subject,
            snippet=snippet,
            received_at=received_at,
            thread_id=thread_id,
            status="saved",
        )
        self.db.add(email)
        self.db.commit()
        self.db.refresh(email)
        return email

    def add_sync_log(self, account_id: int | None, total_processed: int, total_saved: int, total_ignored: int, details: str | None = None) -> None:
        log = SyncLog(
            account_id=account_id,
            total_processed=total_processed,
            total_saved=total_saved,
            total_ignored=total_ignored,
            details=details,
        )
        self.db.add(log)
        self.db.commit()

    def list_processed_emails(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.db.execute(
            select(ProcessedEmail, GmailAccount, EmailCategory)
            .join(GmailAccount, ProcessedEmail.account_id == GmailAccount.id)
            .join(EmailCategory, ProcessedEmail.category_id == EmailCategory.id)
            .order_by(ProcessedEmail.saved_at.desc())
            .limit(limit)
        ).all()

        result: list[dict[str, Any]] = []
        for email, account, category in rows:
            result.append({
                "id": email.id,
                "gmail_message_id": email.gmail_message_id,
                "account": account.email_address,
                "category": category.category_name,
                "subject": email.subject,
                "sender": email.sender_email,
                "snippet": email.snippet,
                "saved_at": email.saved_at,
            })
        return result
