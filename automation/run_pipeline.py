import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import daily_short
from render_patch import render
daily_short.render = render
daily_short.main()
