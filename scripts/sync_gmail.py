from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.db import SessionLocal
from app.models import EmailCategory
from app.sync_service import SyncService


def ensure_categories() -> None:
    db = SessionLocal()
    try:
        existing = db.execute(select(EmailCategory)).scalars().all()
        if existing:
            return

        defaults = [
            ("Trabalho", "trabalho", "Trabalho"),
            ("Processo Seletivo", "processo-seletivo", "Processo Seletivo"),
            ("Faculdade", "faculdade", "Faculdade"),
            ("Propaganda", "propaganda", "Propaganda"),
            ("Banco", "banco", "Banco"),
            ("Outros", "outros", "Outros"),
        ]

        for category_name, slug, label in defaults:
            db.add(EmailCategory(category_name=category_name, slug=slug, label_name=label, active=True))

        db.commit()
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Sincroniza Gmail para persistência e labels.")
    parser.add_argument("--account-name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--account-type", required=True, choices=["pessoal", "profissional", "faculdade"])
    parser.add_argument("--max-results", type=int, default=20)
    args = parser.parse_args()

    ensure_categories()
    db = SessionLocal()
    try:
        sync = SyncService(db)
        result = sync.sync_account(args.account_name, args.email, args.account_type, max_results=args.max_results)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
