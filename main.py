"""Application entry point for running the portfolio dashboard."""

import os
from dotenv import load_dotenv

load_dotenv()

from app import app


def main() -> None:
    port = int(os.getenv("PORT", 5000))
    print("\n  Portfolio Dashboard")
    print("  ───────────────────")
    print(f"  http://localhost:{port}\n")
    app.run(port=port, debug=False)


if __name__ == "__main__":
    main()
