"""Let the tests import build.py and the figure scripts by name."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for extra in (ROOT, ROOT / "figures"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))
