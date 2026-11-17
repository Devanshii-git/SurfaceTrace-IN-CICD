"""Root CLI entrypoint for SurfaceTrace-IN.

Allows running CLI commands directly on Windows/Linux without setting PYTHONPATH:
    python cli.py evaluate
    python cli.py score
    python cli.py export
    python cli.py seed-demo
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from st.cli import app

if __name__ == "__main__":
    app()
