from __future__ import annotations

import json
from pathlib import Path
import sys

from models import NewsStateModel

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

def main() -> None:
    output_path = REPO_ROOT / "contracts" / "news_state.schema.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    schema = NewsStateModel.model_json_schema()
    output_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    print(f"Wrote schema to {output_path}")


if __name__ == "__main__":
    main()
