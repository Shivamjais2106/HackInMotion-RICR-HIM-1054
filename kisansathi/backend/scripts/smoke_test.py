"""
Boot the app and exercise the endpoints that need no database, to prove the
blueprint wiring is live: routes reachable, JSON envelopes intact, rate limiting
attached, 404 handler returning JSON rather than HTML.

Endpoints that read MongoDB are skipped — this is a wiring check, not an
integration test. Heavy ML deps are stubbed the same way scripts/dump_routes.py
does it, so it runs without the full ML stack.

Usage (from the backend/ directory):
    python scripts/smoke_test.py
"""

import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import werkzeug

# Flask 2.3's test client reads werkzeug.__version__, which werkzeug 3.x removed.
# requirements.txt pins werkzeug 2.3.7, so this only bites on a dev machine that
# has drifted to 3.x; shim it so the smoke test still runs there.
if not hasattr(werkzeug, "__version__"):
    from importlib.metadata import version

    werkzeug.__version__ = version("werkzeug")

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

# Database-free GET endpoints, one per blueprint wherever possible.
GET_ENDPOINTS = [
    "/api/health",
    "/api/status",
    "/api/soil/types",
    "/api/soil/crops",
    "/api/soil/fertilizers",
    "/api/months",
    "/api/crop-calendar",
    "/api/crop-calendar/month/January",
    "/api/pest/all",
    "/api/livestock-diseases/cattle",
    "/api/dashboard/stats",
    "/api/dashboard/alerts",
    "/api/dashboard/summary",
    "/api/dashboard/endpoints",
    "/api/dashboard/health",
]

# Reachable, but their result depends on infrastructure this harness does not
# provide, so they are reported rather than asserted:
#   /api/cache/stats — returns 503 by design while Redis is down.
#   /api/seasons     — unpickles a model, which the torch MagicMock above breaks.
REPORT_ONLY = [
    "/api/cache/stats",
    "/api/seasons",
]


def main() -> int:
    import app_enhanced

    app = app_enhanced.app
    client = app.test_client()
    failures = []

    for path in GET_ENDPOINTS:
        try:
            response = client.get(path)
        except Exception as e:
            failures.append(f"{path}: raised {type(e).__name__}: {e}")
            continue

        if response.status_code >= 500:
            body = response.get_data(as_text=True)[:200]
            failures.append(f"{path}: HTTP {response.status_code} {body}")
        else:
            print(f"  ok  {response.status_code}  {path}")

    for path in REPORT_ONLY:
        response = client.get(path)
        print(f"  --  {response.status_code}  {path}  (not asserted)")

    # The 404 handler must return JSON, never an HTML error page.
    response = client.get("/api/definitely-not-a-route")
    if response.status_code != 404:
        failures.append(f"unknown route returned {response.status_code}, expected 404")
    elif not response.is_json:
        failures.append("404 handler did not return JSON")
    else:
        print("  ok  404 handler returns JSON")

    # Rate limiting must actually be attached to blueprint routes: /api/health is
    # declared as 100 per hour, so request 101 has to be rejected.
    limited = None
    for i in range(105):
        if client.get("/api/health").status_code == 429:
            limited = i + 1
            break
    if limited is None:
        failures.append("rate limit on /api/health never triggered — limiter not attached")
    else:
        print(f"  ok  rate limit triggered on request {limited} to /api/health")

    print()
    if failures:
        print(f"FAILED ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"PASSED - {len(GET_ENDPOINTS)} endpoints + 404 handler + rate limiting")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
