from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.classifier import EmailClassifier
from app.gmail_service import GmailService
from app.repository import Repository


class SyncService:
    def __init__(self, db: Session, gmail_service: GmailService | None = None):
        self.db = db
        self.gmail_service = gmail_service or GmailService()
        self.classifier = EmailClassifier()
        self.repository = Repository(db)

    def sync_account(self, account_name: str, email_address: str, account_type: str, max_results: int = 50) -> dict[str, Any]:
        account = self.repository.get_or_create_account(account_name, email_address, account_type)
        message_ids = self.gmail_service.list_messages(user_id="me", max_results=max_results)
        processed = 0
        saved = 0
        ignored = 0

        for item in message_ids:
            message_id = item.get("id")
            if not message_id:
                continue

            summary = self.gmail_service.get_message_summary(message_id, user_id="me")
            sender_email = self._extract_sender_email(summary.get("from", ""))
            subject = summary.get("subject", "")
            snippet = summary.get("snippet", "")
            category_result = self.classifier.classify(sender_email, subject, snippet)

            if not category_result.should_save:
                ignored += 1
                continue

            category = self.repository.get_category_by_name(category_result.category)
            if category is None:
                ignored += 1
                continue

            received_at = self._parse_gmail_date(summary.get("date"))
            self.repository.save_processed_email(
                account_id=account.id,
                category_id=category.id,
                gmail_message_id=message_id,
                sender_email=sender_email,
                sender_name=self._extract_sender_name(summary.get("from", "")),
                subject=subject,
                snippet=snippet,
                received_at=received_at,
                thread_id=summary.get("thread_id"),
            )

            if category_result.move_to_label:
                label_name = category.label_name
                label_id = self._ensure_label(label_name)
                if label_id:
                    self.gmail_service.add_label_to_message(message_id, label_id, user_id="me")

            if category_result.mark_as_read:
                self.gmail_service.mark_as_read(message_id, user_id="me")

            if category_result.should_delete_from_inbox:
                self.gmail_service.archive_message(message_id, user_id="me")

            processed += 1
            saved += 1

        self.repository.add_sync_log(
            account_id=account.id,
            total_processed=processed,
            total_saved=saved,
            total_ignored=ignored,
            details=f"Sincronização concluída para {email_address}",
        )

        return {
            "account": account.email_address,
            "processed": processed,
            "saved": saved,
            "ignored": ignored,
        }

    def _ensure_label(self, label_name: str) -> str | None:
        list_result = self.gmail_service.get_service().users().labels().list(userId="me").execute()
        for label in list_result.get("labels", []):
            if label.get("name") == label_name:
                return label.get("id")
        return self.gmail_service.create_label(label_name, user_id="me")

    def _extract_sender_email(self, from_header: str) -> str:
        if "<" in from_header and ">" in from_header:
            start = from_header.index("<") + 1
            end = from_header.index(">")
            return from_header[start:end].strip()
        return from_header.strip()

    def _extract_sender_name(self, from_header: str) -> str:
        if "<" in from_header and ">" in from_header:
            return from_header.split("<")[0].strip().strip('"')
        return from_header.strip()

    def _parse_gmail_date(self, date_value: str | None) -> datetime | None:
        if not date_value:
            return None
        try:
            return datetime.strptime(date_value, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            return None
