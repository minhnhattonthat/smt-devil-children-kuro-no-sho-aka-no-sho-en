"""One-command check (pre-commit runs this): all tests + text lint + name consistency. Exit code gates the commit."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
py = [sys.executable, '-X', 'utf8']
rc = subprocess.call(py + ['-m', 'pytest', '-q', '-x', str(ROOT / 'tests')], cwd=ROOT)
rc = rc or subprocess.call(py + [str(ROOT / 'tools' / 'names_check.py')], cwd=ROOT)
rc = rc or subprocess.call(py + [str(ROOT / 'tools' / 'cavecheck.py')], cwd=ROOT)
sys.exit(rc)
