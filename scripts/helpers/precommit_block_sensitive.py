from __future__ import annotations
import sys
from pathlib import Path

BLOCK_PREFIXES = (
    Path("data") / "raw",
    Path("data") / "identity_key",
    Path("data") / "upload",
    Path("logs"),
)

def main(files: list[str]) -> int:
    bad = []
    for f in files:
        p = Path(f)
        rel = p.as_posix()
        for pref in BLOCK_PREFIXES:
            if rel.startswith(pref.as_posix()):
                bad.append(rel)
                break
    if bad:
        print("ERROR: sensitive files staged for commit:")
        for b in bad:
            print(" -", b)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
