from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import get_settings
from app.db import SessionLocal
from app.sync_service import SyncService


def _default_accounts():
    settings = get_settings()
    return [
        {
            "account_name": "Pessoal",
            "email_address": settings.personal_account or "marcusadrianomeleiro@gmail.com",
            "account_type": "pessoal",
        },
        {
            "account_name": "Profissional",
            "email_address": settings.professional_account or "meleiro.dev@gmail.com",
            "account_type": "profissional",
        },
        {
            "account_name": "Faculdade",
            "email_address": settings.university_account or "marcus.adriano@sga.pucminas.br",
            "account_type": "faculdade",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Sincroniza todas as contas cadastradas do Gmail.")
    parser.add_argument("--max-results", type=int, default=30)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        sync = SyncService(db)
        results = sync.sync_all_accounts(account_configs=_default_accounts(), max_results=args.max_results)
        for item in results:
            print(item)
    finally:
        db.close()


if __name__ == "__main__":
    main()
