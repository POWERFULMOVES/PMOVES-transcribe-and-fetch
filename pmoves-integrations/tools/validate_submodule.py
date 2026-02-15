#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys

from _pmoves_root import find_pmoves_root


def main() -> int:
    root = find_pmoves_root("pmoves/tools/submodule_integrity.py")
    if not root:
        print("Could not locate PMOVES root. Set PMOVES_ROOT=/path/to/PMOVES.AI")
        return 2

    cmd = [sys.executable, str(root / "pmoves/tools/submodule_integrity.py"), *sys.argv[1:]]
    return subprocess.run(cmd, cwd=root).returncode


if __name__ == "__main__":
    raise SystemExit(main())
