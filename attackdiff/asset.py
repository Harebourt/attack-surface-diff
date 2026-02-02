from datetime import datetime, timezone
from typing import List, Optional


class Asset:
    """
    Represents a single attack surface asset (host/IP) that may persist across scans.
    """

    def __init__(
        self,
        host: str,
        ip: Optional[str] = None,
        ports: Optional[List[int]] = None,
        services: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
    ):
        self.id = host                     # stable identifier
        self.host = host
        self.ip = ip
        self.ports = ports or []
        self.services = services or []
        self.sources = sources or []

        now = datetime.now(timezone.utc).isoformat()
        self.first_seen = now
        self.last_seen = now

    def update_seen(self) -> None:
        """Update last_seen when asset is observed again."""
        self.last_seen = datetime.now(timezone.utc).isoformat()

    def merge(self, other: "Asset") -> None:
        """
        Merge data from another observation of the same asset.
        """
        if other.ip:
            self.ip = other.ip

        self.ports = sorted(set(self.ports + other.ports))
        self.services = sorted(set(self.services + other.services))
        self.sources = sorted(set(self.sources + other.sources))
        self.update_seen()

    def to_dict(self) -> dict:
        """Serialize asset to dictionary."""
        return {
            "id": self.id,
            "host": self.host,
            "ip": self.ip,
            "ports": self.ports,
            "services": self.services,
            "sources": self.sources,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Asset":
        """Recreate Asset object from stored dictionary."""
        asset = cls(
            host=data["host"],
            ip=data.get("ip"),
            ports=data.get("ports", []),
            services=data.get("services", []),
            sources=data.get("sources", []),
        )
        asset.first_seen = data.get("first_seen", asset.first_seen)
        asset.last_seen = data.get("last_seen", asset.last_seen)
        return asset


