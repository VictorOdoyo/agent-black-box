from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


class UtcClock:
    def now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class FrozenClock:
    current: datetime

    @classmethod
    def at(cls, iso_timestamp: str) -> "FrozenClock":
        normalized = iso_timestamp.replace("Z", "+00:00")
        return cls(datetime.fromisoformat(normalized))

    def now(self) -> str:
        return self.current.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    def tick(self, seconds: int = 1) -> str:
        self.current = self.current + timedelta(seconds=seconds)
        return self.now()
