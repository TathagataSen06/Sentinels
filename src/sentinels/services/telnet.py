"""Telnet decoy.

Presents a login prompt and records the username/password pairs submitted by
brute-force bots. A small, configurable number of attempts is allowed, each
answered with ``Login incorrect`` so the client keeps trying and reveals more
of its credential list.
"""

from __future__ import annotations

from .base import BaseService, Session


class TelnetService(BaseService):
    service_type = "telnet"
    default_banner = "Ubuntu 22.04.3 LTS"

    async def handle(self, session: Session) -> None:
        banner = self.banner or self.default_banner
        max_attempts = int(self.option("max_attempts", 3))
        hostname = str(self.option("hostname", "server"))

        if banner and not await session.send(f"{banner}\r\n"):
            return

        for _ in range(max_attempts):
            username = await session.readline(f"{hostname} login: ")
            if username is None:
                return
            password = await session.readline("Password: ")
            if password is None:
                return
            session.emit_login(username=username, password=password)
            if not await session.send("\r\nLogin incorrect\r\n"):
                return
