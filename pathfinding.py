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

    def _get_valid_moves(
        self,
        current_time: int,
        current_pos: Hub | Link,
        came_from: dict[tuple[int, Hub | Link], tuple[int, Hub | Link] | None]
    ) -> list[Hub | Link]:
        """Determines all valid next positions for a given state.

        Args:
            current_time (int): The current turn number.
            current_pos (Hub | Link): The current location.
            came_from (dict): The history of visited states to prevent
            backtracking and determine direction on links.

        Returns:
            list[Hub | Link]: A list of valid next locations.
        """
        valid_moves: list[Hub | Link] = []

        if isinstance(current_pos, Hub):
            for link in self.network_map.adjacency[current_pos.name]:
                if link.hub_1 != current_pos:
                    target = link.hub_1
                else:
                    target = link.hub_2
                if target.zone in ("normal", "priority", "end_hub"):
                    if (self.calendar.get(current_time + 1, {}).get(target, 0)
                            < target.max_drones):
                        valid_moves.append(target)
                elif target.zone == "restricted":
                    if (
                        (self.calendar.get(current_time + 1, {}).get(link, 0)
                         < link.max_link_capacity)
                        and
                        (self.calendar.get(current_time + 2, {}).get(target, 0)
                         < target.max_drones)
                    ):
                        valid_moves.append(link)
            if (self.calendar.get(current_time + 1, {}).get(current_pos, 0)
                    < current_pos.max_drones):
                valid_moves.append(current_pos)

        elif isinstance(current_pos, Link):
            parent = came_from[(current_time, current_pos)]
            if parent is not None:
                parent_pos = parent[1]
                if current_pos.hub_1 != parent_pos:
                    target = current_pos.hub_1
                else:
                    target = current_pos.hub_2
                if (self.calendar.get(current_time + 1, {}).get(target, 0)
                        < target.max_drones):
                    valid_moves.append(target)

        return valid_moves

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
        state: tuple[int, Hub | Link] = (start_time, start_hub)
        queue: deque[tuple[int, Hub | Link]] = deque([state])
        came_from: dict[tuple[int, Hub | Link],
                        tuple[int, Hub | Link] | None] = {
                            (start_time, start_hub): None}

        while queue:
            current_time, current_pos = queue.popleft()
            if current_pos == end_hub:
                path: list[Hub | Link] = []
                curr_state = (current_time, current_pos)
                while True:
                    parent = came_from[curr_state]
                    if parent is None:
                        break
                    path.append(curr_state[1])
                    curr_state = parent
                path.reverse()
                return path
            next_moves = self._get_valid_moves(
                current_time, current_pos, came_from
            )
            next_moves.sort(key=lambda x: x.zone != "priority"
                            if isinstance(x, Hub) else True)
            next_time = current_time + 1

            for target in next_moves:
                new_state = (next_time, target)
                if new_state not in came_from:
                    queue.append(new_state)
                    came_from[new_state] = (current_time, current_pos)
        return None

    def book_path(self, path: list[Hub | Link], start_time: int = 0) -> None:
        """Registers a computed path into the shared calendar
        to prevent collisions.

        Args:
            path (list[Hub | Link]): The sequence of locations
            the drone will traverse.
            start_time (int): The turn number when the drone
            begins its journey.
        """
        for time, node in enumerate(path, start_time + 1):
            self.calendar.setdefault(time, {})
            nb_drones = self.calendar[time].get(node, 0)
            self.calendar[time][node] = nb_drones + 1
