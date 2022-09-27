from typing import Optional

import inflect


class CountAware:
    def __init__(self, fleets: int, ships: int, missiles: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fleets = fleets or 0
        self.ships = ships or 0
        self.missiles = missiles or 0

    @property
    def counts(self) -> Optional[str]:
        counts = []
        p = inflect.engine()
        if self.fleets:
            counts.append(p.no("fleet file", self.fleets))
        if self.ships:
            counts.append(p.no("ship template", self.ships))
        if self.missiles:
            counts.append(p.no("missile template", self.missiles))

        if not counts:
            return None

        if len(counts) == 1:
            return counts[0]

        return p.join(counts)

    @property
    def is_empty(self) -> bool:
        return self.fleets + self.ships + self.missiles == 0


class TimeAware:
    def __init__(self, last_days: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.last_days = last_days

    @property
    def since(self) -> str:
        if self.last_days == 1:
            return "24 hours"
        return f"{self.last_days} days"


class User(CountAware, TimeAware):
    def __init__(self, guild: int, user: int, fleets: int, ships: int, missiles: int, last_days: int) -> None:
        super().__init__(fleets=fleets, ships=ships, missiles=missiles, last_days=last_days)
        self.user = user
        self.guild = guild

    def __str__(self) -> str:
        if not self.counts:
            return ""
        return f"The busiest user has requested an analysis of {self.counts}."


class Guild(CountAware, TimeAware):
    def __init__(self, guilds: int, fleets: int, ships: int, missiles: int, last_days: int, user: User) -> None:
        super().__init__(fleets=fleets, ships=ships, missiles=missiles, last_days=last_days)
        self.guilds = guilds
        self.user = user

    def __str__(self) -> str:
        if self.is_empty:
            return f"In the last {self.since} I have had nothing to do. Blissful life."

        servers = "servers" if self.guilds > 1 else "server"
        return (f"In the last {self.since} I have converted {self.counts} across {self.guilds} {servers}.\n") + str(
            self.user
        )
