"""Map models representing the drone routing network."""


from hub_link_models import NormalHub, PriorityHub, RestrictedHub, \
    BlockedHub, StartHub, EndHub, Link, Hub
from typing import Any, cast
from parsing import LinkData, HubData


class Map:

    def __init__(self, config: dict[str, Any]) -> None:
        """Initializes the network map from a configuration dictionary.

        Args:
            config (dict[str, Any]): The parsed configuration containing
                drones count, hubs data, and connections data.
        """
        self.config = config
        self.nb_drones: int = cast(int, config.get("nb_drones"))
        self.hubs: dict[str, Hub] = {}
        self.adjacency: dict[str, list[Link]] = {}
        self._build_hubs(config)
        self._build_links(config)

    def _build_hubs(self, config: dict[str, Any]) -> None:
        """Instantiates Hub objects and adds them to the map.

        Args:
            config (dict[str, Any]): The parsed configuration.
        """
        if config.get("start_hub"):
            start_data: HubData = config["start_hub"]
            start_hub = StartHub(start_data.name, start_data.x, start_data.y,
                                 start_data.zone, start_data.color)
            self.hubs[start_hub.name] = start_hub
            self.adjacency[start_hub.name] = []
        if config.get("end_hub"):
            end_data: HubData = config["end_hub"]
            end_hub = EndHub(end_data.name, end_data.x, end_data.y,
                             end_data.zone, end_data.color)
            self.hubs[end_hub.name] = end_hub
            self.adjacency[end_hub.name] = []
        for hub_data in config.get("hubs", []):
            pass

    def _build_links(self, config: dict[str, Any]) -> None:
        """Instantiates Link objects and builds the adjacency list.

        Args:
            config (dict[str, Any]): The parsed configuration.
        """
        for link_data in config.get("connections", []):
            pass
