from __future__ import annotations

from fastapi import FastAPI
from sqlalchemy import text

from app.db import Base, engine
from app.models import GmailAccount, ProcessedEmail, EmailCategory

app = FastAPI(title="Gmail Organizer API")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover
        return {"status": "error", "detail": str(exc)}


@app.get("/accounts")
def list_accounts() -> list[dict[str, str | int]]:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, account_name, email_address, account_type FROM gmail_account ORDER BY id"))
        return [
            {"id": row[0], "account_name": row[1], "email_address": row[2], "account_type": row[3]}
            for row in result.fetchall()
        ]


@app.get("/emails")
def list_emails(limit: int = 50) -> list[dict[str, str | int]]:
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT p.id, a.email_address, c.category_name, p.subject, p.sender_email, p.snippet, p.saved_at
                FROM processed_email p
                JOIN gmail_account a ON a.id = p.account_id
                JOIN email_category c ON c.id = p.category_id
                ORDER BY p.saved_at DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        )
        return [
            {
                "id": row[0],
                "account": row[1],
                "category": row[2],
                "subject": row[3],
                "sender": row[4],
                "snippet": row[5],
                "saved_at": str(row[6]),
            }
            for row in result.fetchall()
        ]
