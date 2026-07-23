"""Map models representing the drone routing network."""


from hub_link_models import NormalHub, PriorityHub, RestrictedHub, \
    BlockedHub, StartHub, EndHub, Link, Hub
from typing import Any, cast
from parsing import HubData


class Drone:
    """Represents a drone navigating the network.

    Attributes:
        current_pos (Hub | Link): The current node or edge.
        is_arrived (bool): Flag when the drone reached the end_hub.
        turns_remaining (int): numbers of turns to wait on a link.
    """

    def __init__(self, drone_id: str, start_hub: StartHub,
                 end_hub: EndHub) -> None:
        """Initializes a Drone with an ID and starting position.

        Args:
            drone_id (str): The unique identifier for the drone.
            start_hub (Hub): The initial hub where the drone is spawned.
            end_hub (Hub): The final hub to reach.
        """
        self.drone_id = drone_id
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.current_pos: Hub | Link = start_hub
        self.is_arrived: bool = False
        self.path: list[Hub | Link] = []

    def move(self, target: Hub | Link) -> None:
        """Moves the drone to the specified target.

        Handles the logic for updating the drone's current position,
        and updating the arrival status.

        Args:
            target (Hub | Link): The destination hub or the link to
                transit on.
        """
        if self.is_arrived:
            return
        else:
            self.current_pos = target
            if self.current_pos == self.end_hub:
                self.is_arrived = True


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
            start = StartHub(start_data.name, start_data.x, start_data.y,
                             start_data.zone, start_data.color)
            self.hubs[start.name] = start
            self.start_hub: StartHub = start
            self.adjacency[start.name] = []
        if config.get("end_hub"):
            end_data: HubData = config["end_hub"]
            end = EndHub(end_data.name, end_data.x, end_data.y,
                         end_data.zone, end_data.color)
            self.hubs[end.name] = end
            self.end_hub: EndHub = end
            self.adjacency[end.name] = []
        for hub_data in config.get("hubs", []):
            new_hub: Hub
            match hub_data.zone:
                case "normal":
                    new_hub = NormalHub(
                        hub_data.name, hub_data.x, hub_data.y,
                        color=hub_data.color, max_drones=hub_data.max_drones
                    )
                case "restricted":
                    new_hub = RestrictedHub(
                        hub_data.name, hub_data.x, hub_data.y,
                        hub_data.zone, hub_data.color, hub_data.max_drones
                    )
                case "priority":
                    new_hub = PriorityHub(
                        hub_data.name, hub_data.x, hub_data.y,
                        hub_data.zone, hub_data.color, hub_data.max_drones
                    )
                case "blocked":
                    new_hub = BlockedHub(
                        hub_data.name, hub_data.x, hub_data.y,
                        hub_data.zone, hub_data.color
                    )
                case _:
                    raise ValueError(f"Invalid zone type detected: \
                                     {hub_data.zone}")
            self.hubs[new_hub.name] = new_hub
            self.adjacency[new_hub.name] = []

    def _build_links(self, config: dict[str, Any]) -> None:
        """Instantiates Link objects and builds the adjacency list.

        Args:
            config (dict[str, Any]): The parsed configuration.
        """
        for link_data in config.get("connections", []):
            if (
                link_data.hub_1 in self.hubs and
                link_data.hub_2 in self.hubs
            ):
                new_link = Link(self.hubs[link_data.hub_1],
                                self.hubs[link_data.hub_2],
                                link_data.max_link_capacity)
                self.adjacency[new_link.hub_1.name].append(new_link)
                self.adjacency[new_link.hub_2.name].append(new_link)
            else:
                raise ValueError(f"Invalid connection detected: "
                                 f"{link_data.hub_1} or {link_data.hub_2}"
                                 f"doesn't exist")
