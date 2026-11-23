"""Regenerate docs/v2/PLATFORM_RESEARCH_MATRIX.csv from the claims database."""
import json, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from raffle_edge.edge.platform_comparison import build

ROOT = Path(__file__).resolve().parents[1]
VERIFICATION = {
    "7days-performance": "Partly: 302 automated draws reproducible (May-3 Aug 2026); 464 later draws not independently reproducible; live draws: insufficient information",
    "elite-competitions": "Not possible from public data: physical ball machine; no RNG inputs published",
    "dream-car-giveaways": "Not possible yet: states PHP random_int for automated draws but publishes no seed",
    "rev-comps": "Not possible from public data: ball machine / in-house algorithm; no RNG inputs published",
    "lucky-day-competitions": "Not possible from public data: Google RNG on video; no inputs published",
    "omaze-uk": "Not possible from public data: GLI-certified internal engine; entry codes only",
    "botb": "Not applicable (judged spot-the-ball); manual only",
    "click-competitions": "Manual only (terms)",
    "aspire-competitions": "Not possible from public data: GLI-certified RNG claimed; no inputs published",
}
bl = json.loads((ROOT / "data/seed/collection_blocklist.json").read_text())["hosts"]
n = build(sqlite3.connect(ROOT / "data/db/raffle_edge.sqlite"), bl, VERIFICATION, ROOT / "docs/v2/PLATFORM_RESEARCH_MATRIX.csv",
          terms_unread={"raffall", "raffle-house"})
print(n, "platforms")
