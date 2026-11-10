from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.gmail_service import GmailService


def main() -> None:
    gmail = GmailService()
    messages = gmail.list_messages(max_results=5)
    print(f"Total de mensagens retornadas: {len(messages)}")
    for item in messages:
        message_id = item.get("id")
        if not message_id:
            continue
        summary = gmail.get_message_summary(message_id, user_id="me")
        print("-" * 80)
        print("ID:", message_id)
        print("De:", summary.get("from", ""))
        print("Assunto:", summary.get("subject", ""))
        print("Snippet:", summary.get("snippet", "")[:140])
        print("Label IDs:", summary.get("label_ids", []))


if __name__ == "__main__":
    main()
