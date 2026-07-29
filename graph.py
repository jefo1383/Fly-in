import tkinter as tk
from drone_map_models import Map, Drone
from hub_link_models import StartHub, EndHub, Hub, Link


class SimulationGUI:
    """Handles the graphical user interface using sprites.

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

    def __init__(self, network_map: Map, scale: int = 120) -> None:
        """Initializes the GUI, canvas, and loads sprites.

        Args:
            network_map (Map): The parsed map to be displayed.
            scale (int): The multiplication factor for coordinates.
        """
        self.network_map = network_map
        self.scale = scale
        self.drone_items: dict[str, dict[str, int]] = {}

        self.offset_x: int = 100
        self.offset_y: int = 600
        self.root = tk.Tk()
        self.root.title("Fly-in 42")
        self.canvas = tk.Canvas(self.root, height=1000, width=2700, bg="white")
        self.canvas.pack()
        hub_sprite = tk.PhotoImage(file="Assets/hub.png")
        self.start_hub_sprite = hub_sprite.subsample(4, 4)
        self.end_hub_sprite = hub_sprite.subsample(4, 4)
        self.hub_sprite = hub_sprite.subsample(9, 9)
        h_link_sprite = tk.PhotoImage(file="Assets/h_link.png")
        self.h_link_sprite = h_link_sprite.subsample(30, 30)
        v_link_sprite = tk.PhotoImage(file="Assets/v_link.png")
        self.v_link_sprite = v_link_sprite.subsample(30, 30)
        drone_sprite = tk.PhotoImage(file="Assets/drone.png")
        self.drone_sprite = drone_sprite.subsample(8, 8)

    def _draw_hubs(self) -> None:
        """Draws all hubs from the network map onto the canvas.

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
        """Draws orthogonal links between hubs using sprites.

        Iterates through the network adjacency list and places
        horizontal and vertical link sprites to connect hubs.
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

                    for step_y in range(min(y1_px, y2_px),
                                        (max(y1_px, y2_px) -
                                         (self.v_link_sprite.height() // 2)),
                                        self.v_link_sprite.height()):
                        self.canvas.create_image(x1_px,
                                                 step_y + (self.v_link_sprite.height() // 2) - (self.v_link_sprite.width() // 2),
                                                 image=self.v_link_sprite)
                    # if y1_px != y2_px and x1_px != x2_px:
                        # self.canvas.create_image(x1_px, y2_px,
                        #                         image=self.v_link_sprite)
                    for step_x in range(min(x1_px, x2_px),
                                        (max(x1_px, x2_px) -
                                         (self.h_link_sprite.width() // 2)),
                                        self.h_link_sprite.width()):
                        self.canvas.create_image(step_x + (self.h_link_sprite.width() // 2) + (self.h_link_sprite.height() // 2),
                                                 y2_px,
                                                 image=self.h_link_sprite)

    def _init_drones(self, drones: list[Drone]) -> None:
        """Draws drones and their text IDs at the starting hub.

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
                                                fill="black")
            }

    def update_drone(self, drone_id: str, target: Hub | Link,
                     overlap_index: int = 0) -> None:
        """Updates the position of a specific drone on the canvas.

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
        # Calculer les nouvelles coordonnees en pixels (x_px, y_px)
        if isinstance(target, Hub):
            new_x = target.x
            new_y = target.y
        elif isinstance(target, Link):
            if (target.hub_1.y != target.hub_2.y and
                    target.hub_1.x != target.hub_2.x):
                new_x = target.hub_1.x
                new_y = target.hub_2.y
            elif target.hub_1.x == target.hub_2.x:
                new_x = target.hub_1.x
                new_y = (target.hub_1.y + target.hub_2.y) // 2
            elif target.hub_1.y == target.hub_2.y:
                new_y = target.hub_1.y
                new_x = (target.hub_1.x + target.hub_2.x) // 2
        x_px = (new_x * self.scale) + self.offset_x
        x_px -= (overlap_index * 10)
        y_px = (new_y * self.scale) + self.offset_y
        # Mettre a jour la position avec self.canvas.coords()
        self.canvas.coords(t_id["img"], x_px, y_px)
        self.canvas.coords(t_id["text"], x_px, y_px)

    def setup(self, drones: list[Drone]) -> None:
        """Initializes the visual elements on the canvas in the correct order.

        Draws the links first (background), then the hubs (middle ground),
        and finally places the drones at the starting hub (foreground).

        Args:
            drones (list[Drone]): The list of drones to be placed on the map.
        """
        self._draw_links()
        self._draw_hubs()
        self._init_drones(drones)
