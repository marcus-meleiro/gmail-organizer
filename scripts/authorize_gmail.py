from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google_auth_oauthlib.flow import InstalledAppFlow

from app.config import get_settings
from app.gmail_service import GmailService

settings = get_settings()

SCOPES = [scope.strip() for scope in settings.gmail_scopes.split(',') if scope.strip()]


def _find_credentials_path() -> Path:
    root = Path(__file__).resolve().parent.parent
    candidates = [
        root / "credentials.json",
        root / "app" / "credentials.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Autentica uma conta do Gmail usando OAuth 2.0")
    parser.add_argument("--email", help="E-mail da conta Gmail a ser autenticada", default=None)
    args = parser.parse_args()

    credentials_path = _find_credentials_path()
    if args.email:
        token_path = Path(GmailService.get_account_token_path(args.email))
    else:
        token_path = Path(__file__).resolve().parent.parent / "token.json"

    if not credentials_path.exists():
        raise FileNotFoundError(
            "Arquivo credentials.json não encontrado.\n"
            "1) Crie um projeto no Google Cloud Console\n"
            "2) Ative a Gmail API\n"
            "3) Crie o OAuth Client ID para 'Desktop app'\n"
            f"4) Salve o JSON em uma destas pastas: {credentials_path.parent} ou {Path(__file__).resolve().parent.parent / 'app'}"
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
    creds = flow.run_local_server(port=0)

    with open(token_path, "w", encoding="utf-8") as token_file:
        token_file.write(creds.to_json())

    print(f"Autorização concluída. Token salvo em: {token_path}")
    print("Agora você pode rodar a sincronização do Gmail para essa conta.")


if __name__ == "__main__":
    main()
