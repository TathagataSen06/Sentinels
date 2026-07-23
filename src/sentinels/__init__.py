"""Sentinels — a lightweight, high-signal honeypot framework.

Sentinels stands up low-interaction decoy services on common attacker
target ports, records every interaction as a structured event, and exposes
aggregate telemetry over a Prometheus endpoint for dashboarding and alerting.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "1.0.0"
