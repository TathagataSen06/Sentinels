"""Generic TCP decoy.

A catch-all listener for arbitrary ports. It optionally emits a banner, then
records a bounded preview of whatever the peer sends. Useful for standing up
bait on ports that do not warrant a bespoke protocol emulator (databases,
message queues, proprietary services, and so on).
"""

from __future__ import annotations

from ..events import EventType
from .base import BaseService, Session


class GenericService(BaseService):
    service_type = "generic"
    default_banner = None

    async def handle(self, session: Session) -> None:
        banner = self.banner
        if banner:
            terminator = "\r\n" if self.option("banner_crlf", True) else ""
            if not await session.send(f"{banner}{terminator}"):
                return

        reads = int(self.option("max_reads", 4))
        for _ in range(reads):
            data = await session.read_some(1024)
            if not data:
                return
            session.emit(
                EventType.DATA,
                "payload received",
                length=len(data),
                preview_hex=data[:64].hex(),
                preview_text=data[:64].decode("latin-1", errors="replace"),
            )
