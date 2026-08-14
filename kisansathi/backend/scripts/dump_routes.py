"""
Dump the Flask URL map as a stable, diffable list.

Used to prove a refactor did not change the HTTP surface: capture the output
before a change, capture it after, and diff. Heavy ML dependencies (torch /
torchvision) are stubbed because the route table does not depend on them, so
this runs on a machine without the full ML stack installed.

Usage (from the backend/ directory):
    python scripts/dump_routes.py > /tmp/routes_before.txt
"""

import os
import sys
from unittest.mock import MagicMock

# Import app_enhanced from the backend root regardless of where this is run.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

for name in (
    "torch",
    "torch.nn",
    "torch.nn.functional",
    "torch.optim",
    "torch.utils",
    "torch.utils.data",
    "torchvision",
    "torchvision.transforms",
    "torchvision.models",
    "torchvision.datasets",
):
    sys.modules.setdefault(name, MagicMock())


def main() -> int:
    import app_enhanced

    rules = sorted(
        (
            str(rule.rule),
            ",".join(sorted(m for m in rule.methods if m not in ("HEAD", "OPTIONS"))),
            rule.endpoint,
        )
        for rule in app_enhanced.app.url_map.iter_rules()
    )
    for path, methods, endpoint in rules:
        print(f"{path} [{methods}] -> {endpoint}")
    print(f"# total: {len(rules)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
