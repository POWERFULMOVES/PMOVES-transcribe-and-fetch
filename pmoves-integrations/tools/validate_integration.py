#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from _pmoves_root import find_pmoves_root


def main() -> int:
    root = find_pmoves_root("pmoves/tools/integration_contract_check.py")
    if not root:
        print("Could not locate PMOVES root. Set PMOVES_ROOT=/path/to/PMOVES.AI")
        return 2

    default_target = Path(__file__).resolve().parent.parent
    args = sys.argv[1:]
    target = Path(os.environ.get("INTEGRATION_PATH", str(default_target)))

    passthrough: list[str]
    if args and not args[0].startswith("-"):
        target = Path(args[0])
        passthrough = args[1:]
    else:
        passthrough = args

    cmd = [
        sys.executable,
        str(root / "pmoves/tools/integration_contract_check.py"),
        str(target.resolve()),
        *passthrough,
    ]
    return subprocess.run(cmd, cwd=root).returncode


if __name__ == "__main__":
    raise SystemExit(main())
