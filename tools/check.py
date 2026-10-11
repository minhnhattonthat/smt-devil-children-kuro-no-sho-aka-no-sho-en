"""One-command check (pre-commit runs this): all tests + text lint. Exit code gates the commit."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.exit(subprocess.call([sys.executable, '-X', 'utf8', '-m', 'pytest', '-q', '-x', str(ROOT / 'tests')], cwd=ROOT))
