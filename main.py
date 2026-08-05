"""Contain the engine of the drone routing.

Simulation class, metrics class, and methods which calculate paths,
execute one turn, and the main loop for entry point program.
"""
from drone_map_models import Map, Drone
from hub_link_models import Hub, Link
from pathfinding import Pathfinder
from parsing import parse_arguments, parse_map_file
from graph import SimulationGUI
import time
import tkinter as tk
import sys


class Simulation:
    """Manages the step-by-step execution of the drone routing.

    Attributes:
        network_map (Map): The map of the simulation.
        drones (list[Drone]): The list of active drones.
        gui (SimulationGUI): The graphical interface manager.
    """

    def __init__(self, network_map: Map) -> None:
        """Initialize the simulation with the given map and drones.

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
        """Calculate and books paths for the entire fleet of drones.

        Instantiates the Pathfinder, iterates through all drones,
        finds the optimal path for each, and registers it in the
        shared calendar.
        """
        self.solver = Pathfinder(self.network_map)
        for drone in self.drones:
            path = self.solver.find_path(drone.start_hub, drone.end_hub)
            if path:
                self.solver.book_path(path, drone.start_hub)
                drone.path = path
            else:
                print(f"Error: Disconnected graph or capacity bottleneck.\n"
                      f"No valid path found for drone {drone.drone_id}.")
                sys.exit(1)

    def _play_turn(self) -> list[str]:
        """Execute a single simulation turn for all drones.

        Returns:
            list[str]: A list of movement strings formatted as
                'D<ID>-<destination>' for drones that moved this turn.
        """
        res: list[str] = []
        drones_count: dict[Hub | Link, int] = {}
        moves: list[tuple[Drone, Hub | Link, int]] = []

        for drone in self.drones:
            if not drone.is_arrived:
                target = drone.path.pop(0)
                if target != drone.current_pos:
                    log = f"{drone.drone_id}-{target.name}"
                    res.append(log)
                overlap_index = drones_count.get(target, 0)
                drones_count[target] = overlap_index + 1
                moves.append((drone, target, overlap_index))
                drone.move(target)

        self.gui.animate_drones(moves)
        for m in moves:
            self.gui.update_drone(m[0].drone_id, m[1], m[2])
        return res

    def run(self) -> None:
        """Execute the simulation loop until all drones reach the end."""
        self.route_fleet()
        metrics = Metrics(self.drones)
        try:
            while not all(drone.is_arrived for drone in self.drones):
                metrics.turn_count += 1
                movements = self._play_turn()
                if movements:
                    print(" ".join(movements))
                    self.gui.update_logs(metrics.turn_count, movements)
                self.gui.root.update()
                time.sleep(0.3)
            metrics.print_metrics()
            self.gui.show_final_metrics(metrics.turn_count,
                                        metrics.total_path_cost,
                                        (metrics.total_path_cost /
                                         metrics.turn_count),
                                        metrics.turns_per_drone)
            self.gui.root.mainloop()
        except tk.TclError:
            print("\nProgram interrupted by the user.")


class Metrics:
    """Calculate and stores simulation performance metrics.

    Attributes:
        drones (list[Drone]): The fleet of drones to analyze.
        nb_drones (int): The total number of drones in the fleet.
        total_path_cost (int): The sum of all turns spent by all drones.
    """

    def __init__(self, drones: list[Drone]) -> None:
        """Initialize the metrics based on the initial drone paths.

        Args:
            drones (list[Drone]): The fleet of drones with their
                calculated paths before the simulation starts.
        """
        self.drones = drones
        self.nb_drones: int = len(drones)
        self.turn_count: int = 0
        self.total_path_cost: int = sum(
            sum(1 for i, step in enumerate(drone.path)
                if i == 0 or step != drone.path[i-1]) for drone in drones)
        self.turns_per_drone: float = self.total_path_cost / self.nb_drones

    def print_metrics(self) -> None:
        """Display the calculated metrics.

        Print logs the console and visual representation.
        """
        print(f"\nScore: {self.turn_count} turns")
        print(f"Total path cost: {self.total_path_cost} movements")
        print(f"Average drones moves per turn: {(self.total_path_cost /
                                                self.turn_count):.1f}")
        print(f"Average moves per drone: {self.turns_per_drone:.1f}")


def main() -> None:
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
