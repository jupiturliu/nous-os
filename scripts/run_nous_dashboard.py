#!/usr/bin/env python3
"""Local dashboard server with a run-heartbeat API."""

from __future__ import annotations

import json
import sys
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

from nousos_heartbeat_demo import run_heartbeat_flow


DASHBOARD_PATH = ROOT / "examples" / "runtime" / "dashboard-data.json"


class DashboardHandler(SimpleHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/dashboard-data":
            if DASHBOARD_PATH.exists():
                self._send_json(json.loads(DASHBOARD_PATH.read_text()))
            else:
                self._send_json({"error": "dashboard data not generated yet"}, status=404)
            return
        return super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/run-heartbeat":
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length) if content_length else b"{}"
            try:
                payload = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                payload = {}
            snapshot = run_heartbeat_flow(
                goal=payload.get("goal") or None,
                override_kind=payload.get("override_kind") or None,
            )
            self._send_json(snapshot, status=HTTPStatus.CREATED)
            return
        self._send_json({"error": "not found"}, status=404)


def main() -> None:
    port = 8765
    handler = partial(DashboardHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"NOUS dashboard server listening on http://127.0.0.1:{port}/demo/heartbeat-dashboard.html")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down dashboard server")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
