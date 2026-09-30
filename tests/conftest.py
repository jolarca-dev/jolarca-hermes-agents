"""Shared test configuration."""

import sys
from pathlib import Path

# Add project root to path so tests can import scripts
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))
