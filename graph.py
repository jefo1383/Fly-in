"""Class and methods for visual representation."""
import tkinter as tk
from drone_map_models import Map, Drone
from hub_link_models import StartHub, EndHub, Hub, Link
import time


class SimulationGUI:
    """Handle the graphical user interface using sprites.

    Attributes:
        network_map (Map): The map containing hubs and links.
        root (tk.Tk): The main Tkinter window.
        canvas (tk.Canvas): The drawing area.
        scale (int): The scaling factor for grid coordinates.
        start_hub_sprite (tk.PhotoImage): The sprite image for the start.
        end_hub_sprite (tk.PhotoImage): The sprite image for the end.
        hub_sprite (tk.PhotoImage): The sprite image for hubs.
        h_link_sprite (tk.PhotoImage): Horizontal link sprite.
        v_link_sprite (tk.PhotoImage): Vertical link sprite.
        drone_sprite (tk.PhotoImage): The sprite image for drone.
    """

    def __init__(self, network_map: Map, scale: int = 150) -> None:
        """Initialize the GUI, canvas, and loads sprites.

        Args:
            network_map (Map): The parsed map to be displayed.
            scale (int): The multiplication factor for coordinates.
        """
        self.network_map = network_map
        if len(self.network_map.hubs) > 35:
            self.scale = 100
        else:
            self.scale = scale
        self.drone_items: dict[str, dict[str, int]] = {}

        self.offset_x: int = 100
        self.offset_y: int = 400
        self.root = tk.Tk()
        self.root.title("Fly-in 42")
        if len(self.network_map.hubs) > 8:
            self.canvas = tk.Canvas(self.root, height=1100, width=2700,
                                    bg="white")
        else:
            self.canvas = tk.Canvas(self.root, height=1100, width=1350,
                                    bg="white")
        self.canvas.pack()
        hub_sprite = tk.PhotoImage(file="Assets/hub.png")
        self.start_hub_sprite = hub_sprite.subsample(5, 5)
        self.end_hub_sprite = hub_sprite.subsample(5, 5)
        self.hub_sprite = hub_sprite.subsample(9, 9)
        drone_sprite = tk.PhotoImage(file="Assets/drone.png")
        self.drone_sprite = drone_sprite.subsample(6, 6)

    def _draw_hubs(self) -> None:
        """Draw all hubs from the network map onto the canvas.

        Iterates through the map's hubs, calculates their pixel
        coordinates using the scale factor, draws a colored background,
        and overlays the corresponding sprite.
        """
        for hub in self.network_map.hubs.values():

            x_px = (hub.x * self.scale) + self.offset_x
            y_px = (hub.y * self.scale) + self.offset_y

            if isinstance(hub, StartHub):
                x1 = x_px - (self.start_hub_sprite.width() // 3)
                y1 = y_px - (self.start_hub_sprite.height() // 3)
                x2 = x_px + (self.start_hub_sprite.width() // 3)
                y2 = y_px + (self.start_hub_sprite.height() // 3)
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=hub.color,
                                             outline="")
                self.canvas.create_image(x_px, y_px,
                                         image=self.start_hub_sprite)
            elif isinstance(hub, EndHub):
                x1 = x_px - (self.end_hub_sprite.width() // 3)
                y1 = y_px - (self.end_hub_sprite.height() // 3)
                x2 = x_px + (self.end_hub_sprite.width() // 3)
                y2 = y_px + (self.end_hub_sprite.height() // 3)
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=hub.color,
                                             outline="")
                self.canvas.create_image(x_px, y_px, image=self.end_hub_sprite)
            else:
                x1 = x_px - (self.hub_sprite.width() // 3)
                y1 = y_px - (self.hub_sprite.height() // 3)
                x2 = x_px + (self.hub_sprite.width() // 3)
                y2 = y_px + (self.hub_sprite.height() // 3)
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=hub.color,
                                             outline="")
                self.canvas.create_image(x_px, y_px, image=self.hub_sprite)

    def _draw_links(self) -> None:
        """Draw straight lines between connected hubs.

        Iterates through the network adjacency list and uses the canvas
        to draw direct lines connecting hub_1 and hub_2 for each link
        """
        drawn_links: set[str] = set()

        for list_link in self.network_map.adjacency.values():
            for link in list_link:

                if link.name not in drawn_links:

                    drawn_links.add(link.name)
                    x1_px = (link.hub_1.x * self.scale) + self.offset_x
                    y1_px = (link.hub_1.y * self.scale) + self.offset_y
                    x2_px = (link.hub_2.x * self.scale) + self.offset_x
                    y2_px = (link.hub_2.y * self.scale) + self.offset_y

                    self.canvas.create_line(x1_px, y1_px, x2_px, y2_px,
                                            fill="lightgreen", width=7)

    def _init_drones(self, drones: list[Drone]) -> None:
        """Draw drones and their text IDs at the starting hub.

        Saves their Tkinter IDs in self.drone_items using a nested
        dictionary structure.

        Args:
            drones (list[Drone]): The list of drones on the map.
        """
        x_px = (self.network_map.start_hub.x * self.scale) + self.offset_x
        y_px = (self.network_map.start_hub.y * self.scale) + self.offset_y
        for drone in drones:
            self.drone_items[drone.drone_id] = {
                "img": self.canvas.create_image(x_px, y_px,
                                                image=self.drone_sprite),
                "text": self.canvas.create_text(x_px, y_px,
                                                text=drone.drone_id,
                                                fill="red")
            }

    def update_drone(self, drone_id: str, target: Hub | Link,
                     overlap_index: int = 0) -> None:
        """Update the position of a specific drone on the canvas.

        Retrieves the drone's Tkinter ID, calculates its new pixel
        coordinates based on whether the target is a Hub or a Link,
        applies a visual offset for overlapping drones, and updates
        its position on the canvas.

        Args:
            drone_id (str): The identifier of the drone to move.
            target (Hub | Link): The destination hub or link.
            overlap_index (int): The index of the drone on the target
                to calculate the visual offset (default is 0).
        """
        # Recuperer l'ID Tkinter du drone via self.drone_items
        t_id = self.drone_items[drone_id]
        coords = self._get_target_coords(target, overlap_index)
        # Mettre a jour la position avec self.canvas.coords()
        self.canvas.coords(t_id["img"], coords[0], coords[1])
        self.canvas.coords(t_id["text"], coords[0], coords[1])

    def _get_target_coords(self, target: Hub | Link,
                           overlap_index: int = 0) -> tuple[float, float]:
        if isinstance(target, Hub):
            new_x: float = target.x
            new_y: float = target.y
        elif isinstance(target, Link):
            new_x = (target.hub_1.x + target.hub_2.x) / 2
            new_y = (target.hub_1.y + target.hub_2.y) / 2
        x_px = (new_x * self.scale) + self.offset_x
        x_px -= (overlap_index * 10)
        y_px = (new_y * self.scale) + self.offset_y
        return (x_px, y_px)

    def animate_drones(self, moves: list[tuple[Drone, Hub | Link, int]],
                       frames: int = 25, duration: float = 0.4) -> None:
        """Animate multiple drones moving to their targets simultaneously.

        Args:
            moves (list[tuple[Drone, Hub | Link, int]]): A list of tuples
                containing (drone, target, overlap_index) for this turn.
            frames (int): Total number of intermediate steps for animation.
            duration (float): Total time of the animation in seconds.
        """
        positions: dict[Drone, tuple[float, float]] = {}
        for m in moves:
            curr_x, curr_y = self.canvas.coords(
                self.drone_items[m[0].drone_id]["img"])
            tar_coords = self._get_target_coords(m[1], m[2])
            dx = (tar_coords[0] - curr_x) / frames
            dy = (tar_coords[1] - curr_y) / frames
            positions[m[0]] = (dx, dy)
        try:
            for i in range(frames):
                for drone, dcoord in positions.items():
                    self.canvas.move(
                        self.drone_items[drone.drone_id]["img"],
                        dcoord[0], dcoord[1])
                    self.canvas.move(
                        self.drone_items[drone.drone_id]["text"],
                        dcoord[0], dcoord[1])
                self.root.update()
                time.sleep(duration / frames)
        except tk.TclError:
            pass

    def setup(self, drones: list[Drone]) -> None:
        """Initialize the visual elements on the canvas in the correct order.

        Draws the links first (background), then the hubs (middle ground),
        and finally places the drones at the starting hub (foreground).

        Args:
            drones (list[Drone]): The list of drones to be placed on the map.
        """
        self._draw_links()
        self._draw_hubs()
        self._init_drones(drones)
        self._init_ui_elements()

    def _init_ui_elements(self) -> None:
        """Initialize the UI elements for metrics and logs.

        Creates a Text widget for scrolling logs and embeds it in the canvas.
        Prepares the dictionary for other UI items.
        """
        self.log_widget: tk.Text = tk.Text(self.root, bg="white", fg="black",
                                           bd=5, relief="raised",
                                           font=("liberation mono", 11,
                                                 "bold"))
        self.canvas.create_window(
            int(self.canvas.cget("width")) // 2,
            950, window=self.log_widget, width=int(self.canvas.cget("width")),
            height=300)

    def update_logs(self, turn: int, logs: list[str]) -> None:
        """Append the current turn's movements to the log widget.

        Args:
            turn (int): The current turn number.
            logs (list[str]): Movements of the current turn.
        """
        log_text: str = f"Turn {turn}: " + " ".join(logs) + "\n"
        self.log_widget.insert(tk.END, log_text)
        self.log_widget.see(tk.END)

    def show_final_metrics(
        self,
        score: int,
        path_cost: int,
        avg_moves: float,
        avg_drone: float
    ) -> None:
        """Append the final simulation metrics to the log widget.

        Args:
            score (int): Total number of turns.
            path_cost (int): Total movements made.
            avg_moves (float): Average moves per turn.
            avg_drone (float): Average moves per drone.
        """
        final_text: str = (
            "\n=== SIMULATION COMPLETE ===\n"
            f"Score: {score} turns\n"
            f"Total path cost: {path_cost} movements\n"
            f"Average drones moves per turn: {avg_moves:.1f}\n"
            f"Average moves per drone: {avg_drone:.1f}\n"
        )
        self.log_widget.insert(tk.END, final_text)
        self.log_widget.see(tk.END)
