"""SSH decoy.

A full SSH transport is intentionally *not* implemented — that would be a
high-interaction honeypot with a much larger attack surface. Instead this
service performs the SSH identification-string exchange (RFC 4253 §4.2): it
sends a server banner and captures the client's identification string, which
is a high-signal fingerprint of the scanning tool or bot. The first bytes of
the subsequent key-exchange packet are captured as an opaque preview.
"""

from __future__ import annotations

from ..events import EventType
from .base import BaseService, Session


class SSHService(BaseService):
    service_type = "ssh"
    default_banner = "SSH-2.0-OpenSSH_8.9p1"

    async def handle(self, session: Session) -> None:
        banner = self.banner or self.default_banner
        if not await session.send(f"{banner}\r\n"):
            return

        client_id = await session.readline()
        if client_id is None:
            return
        session.emit(
            EventType.BANNER,
            "ssh client identification",
            client_version=client_id,
        )

        # Capture the opening of the key-exchange without negotiating it.
        payload = await session.read_some(256)
        if payload:
            session.emit(
                EventType.DATA,
                "ssh post-banner payload",
                length=len(payload),
                preview=payload[:64].hex(),
            )
