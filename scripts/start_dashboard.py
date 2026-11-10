from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    env = os.environ.copy()
    env.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
    env.setdefault("STREAMLIT_SERVER_PORT", "8501")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "ui/app.py", "--server.headless", "true", "--server.port", "8501"],
        cwd=str(ROOT),
        env=env,
        check=False,
    )


if __name__ == "__main__":
    main()
