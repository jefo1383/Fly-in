from drone_map_models import Map, Drone


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

    def _play_turn(self) -> list[str]:
        """Executes a single simulation turn for all drones.

        Returns:
            list[str]: A list of movement strings formatted as
                'D<ID>-<destination>' for drones that moved this turn.
        """
        res: list[str] = []
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
