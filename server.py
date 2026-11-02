#!/usr/bin/env python3
"""Local web server for the two-hour daily quote API."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 8765
ROOT = Path(__file__).parent
QUOTES_PATH = ROOT / "data" / "quotes.json"


def load_quotes() -> list[dict[str, str]]:
    try:
        quotes = json.loads(QUOTES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Unable to read {QUOTES_PATH}: {error}") from error

    if not isinstance(quotes, list) or len(quotes) < 2:
        raise RuntimeError(
            "data/quotes.json must contain at least two quotes so adjacent "
            "two-hour slots can always differ."
        )
    if any(
        not isinstance(item, dict)
        or not isinstance(item.get("quote"), str)
        or not item["quote"].strip()
        for item in quotes
    ):
        raise RuntimeError("Each quote must contain a non-empty string named 'quote'.")
    return quotes


def quote_index(slot_key: str, quotes: list[dict[str, str]]) -> int:
    digest = hashlib.sha256(slot_key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % len(quotes)


def current_quote() -> dict[str, object]:
    now = dt.datetime.now().astimezone()
    date_key = now.date().isoformat()
    slot = now.hour // 2
    slot_key = f"{date_key}:{slot}"
    quotes = load_quotes()

    # Keep a stable selection within a slot, while guaranteeing a different
    # quote from the immediately preceding slot.
    index = quote_index(slot_key, quotes)
    previous_slot = (now - dt.timedelta(hours=2)).replace(
        minute=0, second=0, microsecond=0
    )
    previous_key = f"{previous_slot.date().isoformat()}:{previous_slot.hour // 2}"
    previous_index = quote_index(previous_key, quotes)
    if index == previous_index:
        index = (index + 1) % len(quotes)
    quote = quotes[index]
    next_slot_hour = (slot + 1) * 2
    if next_slot_hour == 24:
        next_refresh = (now + dt.timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    else:
        next_refresh = now.replace(
            minute=0, second=0, microsecond=0, hour=next_slot_hour
        )

    return {
        "quote": quote["quote"],
        "author": quote.get("author", ""),
        "date": date_key,
        "slot": slot,
        "nextRefresh": next_refresh.isoformat(),
    }


class QuoteRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        if urlparse(self.path).path == "/api/quote":
            self.send_quote()
            return
        super().do_GET()

    def send_quote(self) -> None:
        try:
            body = json.dumps(current_quote()).encode("utf-8")
        except RuntimeError as error:
            body = json.dumps({"error": str(error)}).encode("utf-8")
            self.send_response(500)
        else:
            self.send_response(200)

        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), QuoteRequestHandler)
    print(f"Daily quotes app running at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()
