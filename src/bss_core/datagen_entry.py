"""Console-script bridge for ``bss-datagen``.

The generator lives at ``src.devtools.datagen.cli`` (importable with the
project root on ``sys.path``, as in tests and ``uv run python``). This
bridge makes it reachable from the installed console script, whose
environment only carries the packaged ``bss_core`` module.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    project_root = str(Path(__file__).resolve().parents[2])
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from src.devtools.datagen.cli import main as cli_main

    return cli_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
