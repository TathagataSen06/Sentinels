"""HTTP decoy.

Serves a convincing but inert administrative login page. Every request is
recorded with its method, path, and salient headers. Credentials arriving via
HTTP Basic auth or an ``application/x-www-form-urlencoded`` POST body are
extracted and recorded as login attempts. No request is ever routed to real
functionality.
"""

from __future__ import annotations

import base64
from urllib.parse import parse_qs

from ..events import EventType
from .base import BaseService, Session

_LOGIN_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body{{font-family:Arial,Helvetica,sans-serif;background:#f2f4f7;margin:0}}
.card{{max-width:340px;margin:8% auto;padding:28px;background:#fff;
border:1px solid #dcdfe4;border-radius:6px}}
h1{{font-size:18px;margin:0 0 18px;color:#233}}
label{{display:block;font-size:13px;color:#556;margin:12px 0 4px}}
input{{width:100%;box-sizing:border-box;padding:9px;border:1px solid #ccd;border-radius:4px}}
button{{margin-top:18px;width:100%;padding:10px;border:0;border-radius:4px;background:#2f6fed;color:#fff;font-size:14px;cursor:pointer}}
.msg{{color:#b3261e;font-size:13px;margin-top:12px}}
</style>
</head>
<body>
<div class="card">
<h1>{title}</h1>
<form method="post" action="/login">
<label for="u">Username</label>
<input id="u" name="username" autocomplete="username">
<label for="p">Password</label>
<input id="p" name="password" type="password" autocomplete="current-password">
<button type="submit">Sign in</button>
{message}
</form>
</div>
</body>
</html>
"""


class HTTPService(BaseService):
    service_type = "http"
    default_banner = "nginx"

    #: Headers surfaced in the structured event (others are counted only).
    _NOTABLE_HEADERS = ("host", "user-agent", "referer", "x-forwarded-for", "cookie")

    async def handle(self, session: Session) -> None:
        request_line = await session.readline()
        if not request_line:
            return

        method, path, version = self._parse_request_line(request_line)
        headers = await self._read_headers(session)
        if headers is None:
            return

        body = b""
        content_length = self._content_length(headers)
        if method in {"POST", "PUT", "PATCH"} and content_length > 0:
            body = await session.read_some(content_length)

        self._record_request(session, method, path, version, headers, body)
        self._record_credentials(session, headers, body)

        await self._respond(session, method)

    # -- parsing ---------------------------------------------------------
    @staticmethod
    def _parse_request_line(line: str) -> tuple[str, str, str]:
        parts = line.split(" ")
        method = parts[0].upper()[:16] if parts else ""
        path = parts[1][:2048] if len(parts) > 1 else "/"
        version = parts[2][:16] if len(parts) > 2 else ""
        return method, path, version

    async def _read_headers(self, session: Session) -> dict[str, str] | None:
        headers: dict[str, str] = {}
        for _ in range(100):  # bound the header count
            line = await session.readline()
            if line is None:
                return None
            if line == "":
                return headers
            name, sep, value = line.partition(":")
            if sep:
                headers[name.strip().lower()] = value.strip()
        return headers

    @staticmethod
    def _content_length(headers: dict[str, str]) -> int:
        try:
            return max(0, int(headers.get("content-length", "0")))
        except ValueError:
            return 0

    # -- recording -------------------------------------------------------
    def _record_request(
        self,
        session: Session,
        method: str,
        path: str,
        version: str,
        headers: dict[str, str],
        body: bytes,
    ) -> None:
        notable = {h: headers[h] for h in self._NOTABLE_HEADERS if h in headers}
        session.emit(
            EventType.HTTP_REQUEST,
            f"{method} {path}",
            method=method,
            path=path,
            http_version=version,
            headers=notable,
            header_count=len(headers),
            body_length=len(body),
        )

    def _record_credentials(
        self, session: Session, headers: dict[str, str], body: bytes
    ) -> None:
        auth = headers.get("authorization", "")
        if auth.lower().startswith("basic "):
            username, password = self._decode_basic(auth[6:])
            if username is not None:
                session.emit_login(
                    username=username, password=password or "", scheme="basic"
                )

        if body and "application/x-www-form-urlencoded" in headers.get(
            "content-type", ""
        ):
            fields = parse_qs(body.decode("latin-1", errors="replace"))
            username = self._first(fields, "username", "user", "login", "email")
            password = self._first(fields, "password", "pass", "passwd")
            if username is not None or password is not None:
                session.emit_login(
                    username=username or "",
                    password=password or "",
                    scheme="form",
                )

    @staticmethod
    def _decode_basic(token: str) -> tuple[str | None, str | None]:
        try:
            decoded = base64.b64decode(token.strip(), validate=True).decode(
                "latin-1", errors="replace"
            )
        except (ValueError, UnicodeDecodeError):
            return None, None
        username, sep, password = decoded.partition(":")
        if not sep:
            return username, None
        return username, password

    @staticmethod
    def _first(fields: dict[str, list[str]], *keys: str) -> str | None:
        for key in keys:
            if fields.get(key):
                return fields[key][0]
        return None

    # -- response --------------------------------------------------------
    async def _respond(self, session: Session, method: str) -> None:
        title = str(self.option("title", "Administration Login"))
        message = (
            '<p class="msg">Invalid username or password.</p>'
            if method in {"POST", "PUT", "PATCH"}
            else ""
        )
        page = _LOGIN_PAGE.format(title=self._escape(title), message=message)
        server = self.banner or self.default_banner
        payload = page.encode("utf-8")
        response = (
            "HTTP/1.1 200 OK\r\n"
            f"Server: {server}\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(payload)}\r\n"
            "Cache-Control: no-store\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        await session.send(response.encode("latin-1", errors="replace") + payload)

    @staticmethod
    def _escape(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
