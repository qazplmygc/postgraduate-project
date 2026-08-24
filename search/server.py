# -*- coding: utf-8 -*-
"""Literature search local server: static page, zone lookup, PDF serving."""

from __future__ import annotations

import json
import re
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from paper_zone import lookup_paper_by_title

SITE_DIR = Path(__file__).resolve().parent
# Project: .../1. literature pdf ; PDF library: D:/刚需
PROJECT_DIR = SITE_DIR.parent
LIT_ROOT = PROJECT_DIR.parent
HOST = "127.0.0.1"
PORT = 8765


class LiteratureHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve project root so /search/ and /patents/ are both reachable.
        super().__init__(*args, directory=str(PROJECT_DIR), **kwargs)

    def log_message(self, format: str, *args) -> None:
        if args and ("/api/" in str(args[0])):
            super().log_message(format, *args)

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.send_response(302)
            self.send_header("Location", "/search/index.html")
            self.end_headers()
            return
        if parsed.path == "/api/lookup":
            self._handle_lookup(parsed.query)
            return
        if parsed.path == "/api/pdf":
            self._handle_pdf(parsed.query)
            return
        if parsed.path == "/api/health":
            self._json_response({"ok": True, "service": "EdgeNexus", "search": True, "patents": True, "reproduce": True, "videos": True, "projects": True, "briefing": True, "waic": True})
            return
        super().do_GET()

    def _json_response(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_lookup(self, query: str) -> None:
        params = urllib.parse.parse_qs(query)
        title = (params.get("title") or [""])[0].strip()
        self._json_response(lookup_paper_by_title(title))

    def _safe_pdf_path(self, rel: str) -> Path | None:
        rel = (rel or "").strip().replace("\\", "/")
        if not rel or rel.startswith("/") or re.search(r"(^|/)\.\.(/|$)", rel):
            return None
        for base in (LIT_ROOT, PROJECT_DIR, SITE_DIR):
            candidate = (base / rel).resolve()
            try:
                candidate.relative_to(base.resolve())
            except ValueError:
                continue
            if candidate.is_file() and candidate.suffix.lower() == ".pdf":
                return candidate
        return None

    def _handle_pdf(self, query: str) -> None:
        params = urllib.parse.parse_qs(query)
        rel = urllib.parse.unquote((params.get("path") or [""])[0])
        path = self._safe_pdf_path(rel)
        if path is None:
            self._json_response({"ok": False, "error": "PDF not found or invalid path"}, 404)
            return
        try:
            data = path.read_bytes()
        except OSError as exc:
            self._json_response({"ok": False, "error": str(exc)}, 500)
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", f'inline; filename="{path.name}"')
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), LiteratureHandler)
    server.allow_reuse_address = True
    print(f"Literature search: http://{HOST}:{PORT}/search/index.html", flush=True)
    print(f"Patents:           http://{HOST}:{PORT}/patents/index.html", flush=True)
    print(f"Reproduce cases:   http://{HOST}:{PORT}/reproduce/index.html", flush=True)
    print(f"Conference videos: http://{HOST}:{PORT}/videos/index.html", flush=True)
    print(f"Projects:          http://{HOST}:{PORT}/projects/index.html", flush=True)
    print(f"Briefing:          http://{HOST}:{PORT}/briefing/index.html", flush=True)
    print(f"WAIC notes:        http://{HOST}:{PORT}/waic/index.html", flush=True)
    print("Ctrl+C to stop", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped", flush=True)
        server.server_close()


if __name__ == "__main__":
    main()
