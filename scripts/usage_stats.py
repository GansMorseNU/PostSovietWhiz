#!/usr/bin/env python3
"""Print app launch and unique-user counts from the deployed sheet.

Usage:
    python3 scripts/usage_stats.py <readback_token>

Hits ?kind=usage_stats on the Apps Script and prints:
  - total launches and total distinct clients (all time)
  - daily: launches per day and distinct clients per day
  - monthly: launches per month and distinct clients per month

"Launch" = one session_start event. "Unique clients" = distinct client_id values
(stable UUID stored in the app's localStorage on first use).
"""

import json
import sys
import urllib.parse
import urllib.request

ENDPOINT = "https://script.google.com/macros/s/AKfycbwayTJFG-d5Nzz7YfBlYUfiOapNbGV0rNvvD_yYMYCBEcFF2uzHbZxYIKgGTDZ8rU5w/exec"


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: usage_stats.py <readback_token>", file=sys.stderr)
        return 2
    token = sys.argv[1]
    qs = urllib.parse.urlencode({"token": token, "kind": "usage_stats"})
    url = f"{ENDPOINT}?{qs}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.load(resp)
    if not data.get("ok"):
        print(f"readback failed: {data}", file=sys.stderr)
        return 1

    print(f"Total launches (all time): {data.get('total_launches', 0)}")
    print(f"Total unique clients (all time): {data.get('total_clients', 0)}")

    daily = data.get("daily", [])
    if daily:
        print("\n=== Daily ===")
        print(f"{'day':<12}{'launches':>10}{'unique':>10}")
        print("-" * 32)
        for row in daily:
            print(f"{row['day']:<12}{row['launches']:>10}{row['unique_clients']:>10}")

    monthly = data.get("monthly", [])
    if monthly:
        print("\n=== Monthly ===")
        print(f"{'month':<10}{'launches':>10}{'unique':>10}")
        print("-" * 30)
        for row in monthly:
            print(f"{row['month']:<10}{row['launches']:>10}{row['unique_clients']:>10}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
