"""Core data models for the Fly-in simulation network."""

from abc import ABC


class Hub(ABC):
    """Abstract base class representing a generic zone in the network.

    Attributes:
        name (str): The unique name of the zone.
        x (int): The X coordinate on the grid.
        y (int): The Y coordinate on the grid.
        max_drones (int): Maximum number of drones allowed simultaneously.
    """

    def __init__(self, name: str, x: int, y: int,
                 max_drones: int | float = 1) -> None:
        """Initializes a Hub with coordinates and capacity."""
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.max_drones: int | float = max_drones


class NormalHub(Hub):
    """A standard zone with a movement cost of 1 turn."""
    pass


class PriorityHub(Hub):
    """A preferred zone with a movement cost of 1 turn."""
    pass


class RestrictedHub(Hub):
    """A sensitive zone with a movement cost of 2 turns."""
    pass


class BlockedHub(Hub):
    """An inaccessible zone. Drones cannot enter."""

    def __init__(self, name: str, x: int, y: int) -> None:
        """Initializes a BlockedHub with a capacity of 0."""
        super().__init__(name, x, y, max_drones=0)


class StartHub(Hub):
    """A start zone with no max_drone limit"""

    def __init__(self, name: str, x: int, y: int) -> None:
        super().__init__(name, x, y, max_drones=float('inf'))


class EndHub(Hub):
    """A end zone with no max_drone limit"""

    def __init__(self, name: str, x: int, y: int) -> None:
        super().__init__(name, x, y, max_drones=float('inf'))


class Link:
    """A bidirectional connection between two hubs.

    Attributes:
        hub_a (Hub): The first connected zone.
        hub_b (Hub): The second connected zone.
        capacity (int): Max drones that can traverse simultaneously.
    """

    def __init__(self, hub_a: Hub, hub_b: Hub, capacity: int = 1) -> None:
        """Initializes a Link with its connected hubs and capacity."""
        self.hub_a: Hub = hub_a
        self.hub_b: Hub = hub_b
        self.capacity: int = capacity
