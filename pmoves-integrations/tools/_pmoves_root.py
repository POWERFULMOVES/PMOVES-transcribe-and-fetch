from __future__ import annotations

import os
from pathlib import Path


def find_pmoves_root(required_relative: str) -> Path | None:
    env_root = os.environ.get("PMOVES_ROOT")
    if env_root:
        candidate = Path(env_root).resolve()
        if (candidate / required_relative).is_file():
            return candidate

    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / required_relative).is_file():
            return parent
    return None
