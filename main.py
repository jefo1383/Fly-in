from drone_map_models import Map, Drone
from hub_link_models import Hub, Link
from pathfinding import Pathfinder
from parsing import parse_arguments, parse_map_file
from graph import SimulationGUI
import time


class Simulation:
    """Manages the step-by-step execution of the drone routing.

    Attributes:
        network_map (Map): The map of the simulation.
        drones (list[Drone]): The list of active drones.
        gui (SimulationGUI): The graphical interface manager.
    """

    def __init__(self, network_map: Map) -> None:
        """Initializes the simulation with the given map and drones.

        Args:
            network_map (Map): The parsed map containing hubs and links.
        """
        self.network_map: Map = network_map
        self.drones: list[Drone] = []

        for i in range(1, self.network_map.nb_drones + 1):
            self.drones.append(
                Drone(f"D{i}", network_map.start_hub, network_map.end_hub)
            )

        self.gui = SimulationGUI(self.network_map)
        self.gui.setup(self.drones)

    def route_fleet(self) -> None:
        """Calculates and books paths for the entire fleet of drones.

        Instantiates the Pathfinder, iterates through all drones,
        finds the optimal path for each, and registers it in the
        shared calendar.
        """
        solver = Pathfinder(self.network_map)
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
        drones_count: dict[Hub | Link, int] = {}
        for drone in self.drones:
            if not drone.is_arrived:
                target = drone.path.pop(0)
                if target != drone.current_pos:
                    log = f"{drone.drone_id}-{target.name}"
                    res.append(log)
                drone.move(target)
                overlap_index = drones_count.get(target, 0)
                drones_count[target] = overlap_index + 1
                self.gui.update_drone(drone.drone_id, target, overlap_index)
        return res

    def run(self) -> None:
        """Executes the simulation loop until all drones reach the end."""
        self.route_fleet()
        metrics = Metrics(self.drones)
        while not all(drone.is_arrived for drone in self.drones):
            metrics.turn_count += 1
            movements = self._play_turn()
            if movements:
                print(" ".join(movements))
            self.gui.root.update()
            time.sleep(0.7)
        metrics.print_metrics()
        self.gui.root.mainloop()


class Metrics:
    """Calculates and stores simulation performance metrics.

    Attributes:
        drones (list[Drone]): The fleet of drones to analyze.
        nb_drones (int): The total number of drones in the fleet.
        total_path_cost (int): The sum of all turns spent by all drones.
    """
    def __init__(self, drones: list[Drone]) -> None:
        """Initializes the metrics based on the initial drone paths.

        Args:
            drones (list[Drone]): The fleet of drones with their
                calculated paths before the simulation starts.
        """
        self.drones = drones
        self.nb_drones: int = len(drones)
        self.turn_count: int = 0
        self.total_path_cost: int = sum(len(drone.path) for drone in drones)
        self.turns_per_drone: float = self.total_path_cost / self.nb_drones

    def print_metrics(self) -> None:
        """Displays the calculated metrics to the console
        and visual representation.
        """
        print(f"Score: {self.turn_count} turns")
        print(f"Total path cost: {self.total_path_cost} movements")
        print(f"Average drones moves per turn: {(self.total_path_cost /
                                                self.turn_count):.1f}")
        print(f"Average moves per drone: {self.turns_per_drone:.1f}")


def main():
    """Entry point of the Fly-in simulation.

    Parses command-line arguments to get the map file,
    generates the configuration dictionary, builds the network map,
    and executes the simulation.
    """
    try:
        print("Hello from fly-in!")
        file_path = parse_arguments()
        config = parse_map_file(file_path)
        network_map = Map(config)
        simulation = Simulation(network_map)
        simulation.run()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
