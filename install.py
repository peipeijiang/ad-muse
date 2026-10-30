#!/usr/bin/env python3
"""AdMuse installer: copy ad-muse and its companion skills into ~/.agents/skills.

Usage:
  python3 install.py --check     # report only
  python3 install.py             # add what is missing; never overwrite
"""
import runpy
import sys
from pathlib import Path

script = Path(__file__).resolve().parent / "skills" / "ad-muse" / "scripts" / "install_dependencies.py"
sys.argv[0] = str(script)
runpy.run_path(str(script), run_name="__main__")
