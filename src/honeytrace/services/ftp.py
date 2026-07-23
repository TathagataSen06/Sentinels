"""FTP decoy.

Implements just enough of RFC 959 to look like a real FTP server to a
scanner: it greets with a 220, answers a handful of pre-auth commands, and
records every ``USER``/``PASS`` pair before returning ``530 Login incorrect``.
No filesystem, data connection, or post-auth command is ever exposed.
"""

from __future__ import annotations

from .base import BaseService, Session


class FTPService(BaseService):
    service_type = "ftp"
    default_banner = "FTP server ready"

    async def handle(self, session: Session) -> None:
        banner = self.banner or self.default_banner
        if not await session.send(f"220 {banner}\r\n"):
            return

        pending_user: str | None = None
        while True:
            line = await session.readline()
            if line is None:
                return
            parts = line.split(" ", 1)
            command = parts[0].upper()
            argument = parts[1].strip() if len(parts) > 1 else ""

            if command == "USER":
                pending_user = argument
                ok = await session.send("331 Please specify the password.\r\n")
            elif command == "PASS":
                session.emit_login(
                    username=pending_user or "",
                    password=argument,
                    command="PASS",
                )
                pending_user = None
                ok = await session.send("530 Login incorrect.\r\n")
            elif command == "QUIT":
                await session.send("221 Goodbye.\r\n")
                return
            elif command == "SYST":
                ok = await session.send("215 UNIX Type: L8\r\n")
            elif command in {"FEAT", "OPTS"}:
                ok = await session.send("211 No features.\r\n")
            elif command in {"AUTH", "PBSZ", "PROT"}:
                ok = await session.send("530 Please login with USER and PASS.\r\n")
            else:
                ok = await session.send("530 Please login with USER and PASS.\r\n")

            if not ok:
                return
