import sys
from pathlib import Path

TASK3_DIR = Path(__file__).resolve().parents[1]
if str(TASK3_DIR) not in sys.path:
    sys.path.insert(0, str(TASK3_DIR))
