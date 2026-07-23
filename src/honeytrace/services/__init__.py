"""Service registry and factory.

Maps the ``type`` key from configuration to a concrete :class:`BaseService`
implementation. Adding a new decoy is a matter of defining the class and
registering it here.
"""

from __future__ import annotations

from ..config import ServiceConfig
from .base import BaseService, ServiceContext, Session
from .ftp import FTPService
from .generic import GenericService
from .http import HTTPService
from .ssh import SSHService
from .telnet import TelnetService

__all__ = [
    "BaseService",
    "ServiceContext",
    "Session",
    "SERVICE_TYPES",
    "create_service",
    "available_types",
]

SERVICE_TYPES: dict[str, type[BaseService]] = {
    cls.service_type: cls
    for cls in (
        SSHService,
        TelnetService,
        FTPService,
        HTTPService,
        GenericService,
    )
}


class UnknownServiceError(ValueError):
    """Raised when a configuration references an unregistered service type."""


def available_types() -> list[str]:
    return sorted(SERVICE_TYPES)


def create_service(config: ServiceConfig, context: ServiceContext) -> BaseService:
    """Instantiate the service implementation named by ``config.type``."""
    try:
        service_cls = SERVICE_TYPES[config.type]
    except KeyError:
        raise UnknownServiceError(
            f"unknown service type {config.type!r}; "
            f"available types: {', '.join(available_types())}"
        ) from None
    return service_cls(config, context)
