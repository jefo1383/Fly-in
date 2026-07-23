from drone_map_models import Map, Drone
from pathfinding import Pathfinder


class Simulation:
    """Manages the step-by-step execution of the drone routing.

    Attributes:
        drones (list[Drones]): The list of drones on the map.
        turn_count (int): The number of turns executed.
    """

    def __init__(self, network_map: Map) -> None:
        """Initializes the simulation with the given map and drones.

        Args:
            network_map (Map): The parsed map containing hubs and links.
        """
        self.network_map: Map = network_map
        self.drones: list[Drone] = []
        self.turn_count: int = 0

        for i in range(1, self.network_map.nb_drones + 1):
            self.drones.append(
                Drone(f"D{i}", network_map.start_hub, network_map.end_hub)
            )

    def route_fleet(self) -> None:
        """Calculates and books paths for the entire fleet of drones.

        Instantiates the Pathfinder, iterates through all drones,
        finds the optimal path for each, and registers it in the
        shared calendar.
        """
        # TODO: Instancier le Pathfinder avec la carte du réseau
        solver = Pathfinder(self.network_map)
        # TODO: Parcourir chaque drone de la flotte
        # TODO: Trouver le chemin, le réserver et l'assigner au drone
        for drone in self.drones:
            path = solver.find_path(drone.start_hub, drone.end_hub)
            if path:
                solver.book_path(path)
                drone.path = path

    def _play_turn(self) -> list[str]:
        """Executes a single simulation turn for all drones.

        Returns:
            list[str]: A list of movement strings formatted as
                'D<ID>-<destination>' for drones that moved this turn.
        """
        res: list[str] = []
        for drone in self.drones:
            if not drone.is_arrived:
                target = drone.path.pop(0)
                drone.move(target)
                log = f"{drone.drone_id}-{target.name}"
                res.append(log)
        return res

    def run(self) -> None:
        """Executes the simulation loop until all drones reach the end."""
        while not all(drone.is_arrived for drone in self.drones):

            self.turn_count += 1
            movements = self._play_turn()
            if movements:
                print(" ".join(movements))


def main():
    print("Hello from fly-in!")


if __name__ == "__main__":
    main()
