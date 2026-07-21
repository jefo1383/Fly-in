from drone_map_models import Map
from hub_link_models import Hub, Link
from typing import Optional
from collections import deque


class Pathfinder:
    """Handles advanced routing for the drone fleet
    using time-space reservations.

    Attributes:
        network_map (Map): The map containing hubs and links.
        calendar (dict[int, dict[Hub | Link, int]]):
        The shared reservation schedule.
    """

    def __init__(self, network_map: Map) -> None:
        """Initializes the pathfinder with the map and an empty schedule.

        Args:
            network_map (Map): The map containing hubs and links.
        """
        self.network_map: Map = network_map
        # Calendrier partagé : Temps -> (Lieu -> Nombre de drones prévus)
        self.calendar: dict[int, dict[Hub | Link, int]] = {}

    def find_path(self, start_hub: Hub, end_hub: Hub,
                  start_time: int = 0) -> Optional[list[Hub | Link]]:
        """Finds a spatio-temporal path for a single drone.

        Uses a Breadth-First Search (BFS) approach adapted for time,
        checking the shared calendar to avoid capacity conflicts.

        Args:
            start_hub (Hub): The drone's starting location.
            end_hub (Hub): The drone's destination.
            start_time (int): The current simulation turn.

        Returns:
            Optional[list[Hub | Link]]: The sequence of hubs and links
                to traverse, or None if no path is found.
        """
        # Etat de depart : un tuple contenant (start_time, start_hub)
        state: tuple[int, Hub | Link] = (start_time, start_hub)
        queue: deque[tuple[int, Hub | Link]] = deque([state])
        came_from: dict[tuple[int, Hub | Link],
                        tuple[int, Hub | Link] | None] = {
                            (start_time, start_hub): None}

        while queue:
            time, pos = queue.popleft()
            if pos == end_hub:
                break
            
