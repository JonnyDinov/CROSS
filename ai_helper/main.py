from __future__ import annotations

import sys

from ai_helper.ui.app import run_app


def main() -> None:
    try:
        run_app()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
