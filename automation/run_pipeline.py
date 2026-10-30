import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import daily_short
from render_patch import render

# Anthropic does not provide a stable official RSS endpoint; avoid a known 404.
daily_short.FEEDS = [feed for feed in daily_short.FEEDS if "anthropic.com/news/rss.xml" not in feed]
daily_short.render = render
daily_short.main()
