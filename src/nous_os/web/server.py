"""Python local Web composition preserving the public route Interface."""

from __future__ import annotations

import json
import mimetypes
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from nous_os.core.context import HarnessContext
from nous_os.web.hermes import HermesGatewayError, ask_hermes, load_local_env, resolve_url


MAX_REQUEST_BYTES = 64_000


def create_server(
    context: HarnessContext,
    *,
    static_root: str | Path,
    host: str = "127.0.0.1",
    port: int = 8787,
) -> ThreadingHTTPServer:
    root = Path(static_root).resolve()
    handler = _handler_type(context, root)
    return ThreadingHTTPServer((host, port), handler)


def serve(context: HarnessContext, *, static_root: str | Path, host: str = "127.0.0.1", port: int = 8787) -> None:
    load_local_env()
    server = create_server(context, static_root=static_root, host=host, port=port)
    print(f"NOUS OS web backend: http://{host}:{server.server_port}")
    print(f"Hermes API server: {resolve_url()}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down NOUS OS web backend")
    finally:
        server.server_close()


def _handler_type(context: HarnessContext, static_root: Path):
    class Handler(BaseHTTPRequestHandler):
        server_version = "NOUSOS/0.2"

        def do_OPTIONS(self) -> None:  # noqa: N802
            if self._path().startswith("/api/"):
                self.send_response(HTTPStatus.NO_CONTENT)
                self._cors_headers()
                self.end_headers()
                return
            self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

        def do_GET(self) -> None:  # noqa: N802
            path = self._path()
            if path == "/api/health":
                self._json(HTTPStatus.OK, {
                    "status": "ok",
                    "service": "nous-os-web-backend",
                    "hermes_api_server_configured": bool(resolve_url()),
                    "hermes_api_server_key_source": "local-env" if os.environ.get("HERMES_API_SERVER_KEY") else "none",
                    "route": "web-backend-to-hermes-gateway",
                    "profile": context.profile_name,
                })
            elif path == "/api/dashboard-data":
                source = context.paths.projections / "dashboard-data.json"
                if not source.exists():
                    self._json(HTTPStatus.NOT_FOUND, {"error": "dashboard data not generated yet"})
                else:
                    self._json(HTTPStatus.OK, json.loads(source.read_text(encoding="utf-8")))
            elif path == "/api/student-sandbox-session":
                self._get_student_session()
            elif path.startswith("/api/"):
                self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            else:
                self._static(path)

        def do_POST(self) -> None:  # noqa: N802
            path = self._path()
            try:
                body = self._body()
            except ValueError as error:
                self._json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                return
            if path == "/api/run-heartbeat":
                if not context.has("heartbeat"):
                    self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "Heartbeat is not enabled by this Profile."})
                    return
                snapshot = context.resolve("heartbeat").run(
                    goal=body.get("goal") or None,
                    override_kind=body.get("override_kind") or None,
                    demo_mode=body.get("demo_mode") or None,
                )
                self._json(HTTPStatus.CREATED, snapshot)
            elif path == "/api/hermes-student-agent":
                try:
                    self._json(HTTPStatus.OK, ask_hermes(body))
                except ValueError as error:
                    self._json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                except HermesGatewayError as error:
                    self._json(error.status, {"error": str(error)})
                except Exception as error:
                    self._json(HTTPStatus.BAD_GATEWAY, {"error": f"Hermes backend server failed: {error}"})
            elif path == "/api/student-sandbox-session":
                if not context.has("student-sandbox"):
                    self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "Student Sandbox is not enabled by this Profile."})
                    return
                record = context.resolve("student-sandbox").save(body)
                self._json(HTTPStatus.OK, {
                    "status": "saved",
                    "session_id": record["session_id"],
                    "saved_at": record["saved_at"],
                    "private_pattern_detected": record["privacy"]["private_pattern_detected"],
                    "storage": record["storage"],
                })
            else:
                self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

        def _get_student_session(self) -> None:
            if not context.has("student-sandbox"):
                self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "Student Sandbox is not enabled by this Profile."})
                return
            query = parse_qs(urlsplit(self.path).query)
            store = context.resolve("student-sandbox")
            if query.get("list") == ["1"]:
                try:
                    limit = int(query.get("limit", ["20"])[0])
                except ValueError:
                    limit = 20
                self._json(HTTPStatus.OK, {"sessions": store.list(limit)})
                return
            session_id = query.get("session_id", [""])[0]
            record = store.read(session_id)
            if record is None:
                self._json(HTTPStatus.NOT_FOUND, {"error": "Student sandbox session not found."})
                return
            if query.get("format") == ["markdown"]:
                self._text(HTTPStatus.OK, _review_markdown(record), "text/markdown; charset=utf-8")
                return
            self._json(HTTPStatus.OK, record)

        def _body(self) -> dict:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as error:
                raise ValueError("Invalid Content-Length.") from error
            if length > MAX_REQUEST_BYTES:
                raise ValueError("Request body too large.")
            try:
                value = json.loads(self.rfile.read(length) if length else b"{}")
            except json.JSONDecodeError as error:
                raise ValueError("Invalid JSON request body.") from error
            if not isinstance(value, dict):
                raise ValueError("JSON request body must be an object.")
            return value

        def _path(self) -> str:
            return urlsplit(self.path).path

        def _cors_headers(self) -> None:
            self.send_header("Access-Control-Allow-Origin", os.environ.get("HERMES_ALLOWED_ORIGIN", "https://nousos.ai"))
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def _json(self, status: int, payload) -> None:
            self._text(status, json.dumps(payload, ensure_ascii=False), "application/json; charset=utf-8")

        def _text(self, status: int, body: str, content_type: str) -> None:
            encoded = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self._cors_headers()
            self.end_headers()
            self.wfile.write(encoded)

        def _static(self, path: str) -> None:
            relative = unquote(path).lstrip("/") or "index.html"
            if relative.endswith("/"):
                relative += "index.html"
            candidate = (static_root / relative).resolve()
            if static_root != candidate and static_root not in candidate.parents:
                self._text(HTTPStatus.FORBIDDEN, "Forbidden", "text/plain; charset=utf-8")
                return
            if not candidate.is_file():
                self._text(HTTPStatus.NOT_FOUND, "Not found", "text/plain; charset=utf-8")
                return
            content_type = mimetypes.guess_type(candidate)[0] or "application/octet-stream"
            data = candidate.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format: str, *args) -> None:
            if os.environ.get("NOUS_OS_WEB_LOG"):
                super().log_message(format, *args)

    return Handler


def _review_markdown(record: dict) -> str:
    worksheet = record.get("worksheet", {})
    readiness = record.get("readiness", {})
    return "\n".join((
        "# Student Sandbox v1 Trial Review",
        "",
        f"- Session id: {record.get('session_id', '[not filled]')}",
        f"- Saved at: {record.get('saved_at', '[not filled]')}",
        "- Privacy: de-identified; no student name, school, email, phone, address, or raw private prompt",
        "",
        "## Session Summary",
        "",
        f"- Research question: {worksheet.get('question') or '[not filled]'}",
        f"- Human boundary: {worksheet.get('boundary') or '[not filled]'}",
        f"- Revised plan: {worksheet.get('revised_plan') or '[not filled]'}",
        "",
        "## Readiness Snapshot",
        "",
        f"- Ready for review: {'yes' if readiness.get('ready_for_review') else 'no'}",
        "",
    ))
