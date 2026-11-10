from __future__ import annotations

import base64
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.config import get_settings

settings = get_settings()

SCOPES = [scope.strip() for scope in settings.gmail_scopes.split(',') if scope.strip()]


class GmailService:
    def __init__(self, credentials_path: str = "credentials.json", token_path: str | None = None) -> None:
        self.credentials_path = credentials_path
        self.token_path = token_path or "token.json"

    def _get_credentials(self) -> Credentials:
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(self.token_path, "w", encoding="utf-8") as token_file:
                    token_file.write(creds.to_json())

        return creds

    def get_service(self):
        creds = self._get_credentials()
        return build("gmail", "v1", credentials=creds)

    def list_messages(self, user_id: str = "me", max_results: int = 100) -> list[dict[str, Any]]:
        service = self.get_service()
        results = service.users().messages().list(userId=user_id, maxResults=max_results).execute()
        return results.get("messages", [])

    def get_message(self, message_id: str, user_id: str = "me") -> dict[str, Any]:
        service = self.get_service()
        return service.users().messages().get(userId=user_id, id=message_id, format="full").execute()

    def get_message_summary(self, message_id: str, user_id: str = "me") -> dict[str, Any]:
        payload = self.get_message(message_id, user_id=user_id)
        headers = payload.get("payload", {}).get("headers", [])
        body = self._extract_body(payload)

        header_map = {h.get("name", "").lower(): h.get("value", "") for h in headers}

        return {
            "id": payload.get("id"),
            "thread_id": payload.get("threadId"),
            "label_ids": payload.get("labelIds", []),
            "subject": header_map.get("subject", ""),
            "from": header_map.get("from", ""),
            "date": header_map.get("date", ""),
            "snippet": payload.get("snippet", ""),
            "body": body,
        }

    def _extract_body(self, payload: dict[str, Any]) -> str:
        parts = payload.get("payload", {}).get("parts", [])
        body_text = ""

        if not parts:
            return ""

        for part in parts:
            mime_type = part.get("mimeType", "")
            if mime_type.startswith("text/"):
                data = part.get("body", {}).get("data")
                if data:
                    decoded = base64.urlsafe_b64decode(data.encode("ASCII") + b"=")
                    body_text += decoded.decode("utf-8", errors="ignore")
        return body_text

    def create_label(self, label_name: str, user_id: str = "me") -> str | None:
        service = self.get_service()
        label = {
            "name": label_name,
            "messageListVisibility": "show",
            "labelListVisibility": "labelShow",
        }
        result = service.users().labels().create(userId=user_id, body=label).execute()
        return result.get("id")

    def add_label_to_message(self, message_id: str, label_id: str, user_id: str = "me") -> None:
        service = self.get_service()
        body = {"addLabelIds": [label_id], "removeLabelIds": ["INBOX"]}
        service.users().messages().modify(userId=user_id, id=message_id, body=body).execute()

    def mark_as_read(self, message_id: str, user_id: str = "me") -> None:
        service = self.get_service()
        body = {"removeLabelIds": ["UNREAD"]}
        service.users().messages().modify(userId=user_id, id=message_id, body=body).execute()

    def archive_message(self, message_id: str, user_id: str = "me") -> None:
        service = self.get_service()
        body = {"removeLabelIds": ["INBOX"]}
        service.users().messages().modify(userId=user_id, id=message_id, body=body).execute()

    @staticmethod
    def get_account_token_path(account_email: str | None = None) -> str:
        base = Path(__file__).resolve().parent.parent
        if account_email:
            safe_name = account_email.replace('@', '_at_').replace('.', '_dot_')
            return str(base / f"token_{safe_name}.json")
        return str(base / "token.json")

    @classmethod
    def for_account(cls, account_email: str, credentials_path: str = "credentials.json") -> "GmailService":
        return cls(credentials_path=credentials_path, token_path=cls.get_account_token_path(account_email))
