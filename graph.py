import tkinter as tk
from drone_map_models import Map


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

    def __init__(self, network_map: Map, scale: int = 100) -> None:
        """Initializes the GUI, canvas, and loads sprites.

        Args:
            network_map (Map): The parsed map to be displayed.
            scale (int): The multiplication factor for coordinates.
        """
        self.network_map = network_map
        self.scale = scale

        self.root = tk.Tk()
        self.root.title("Fly-in 42")
        self.canvas = tk.Canvas(self.root, height=1200, width=1800)
        self.canvas.pack()
        self.start_hub_sprite = tk.PhotoImage(file="Assets/start_hub.png")
        self.end_hub_sprite = tk.PhotoImage(file="Assets/end_hub.png")
        self.hub_sprite = tk.PhotoImage(file="Assets/hub.png")
        self.h_link_sprite = tk.PhotoImage(file="Assets/h_link.png")
        self.v_link_sprite = tk.PhotoImage(file="Assets/v_link.png")
        self.drone_sprite = tk.PhotoImage(file="Assets/drone.png")

    def _draw_hubs(self) -> None:
        """Draws all hubs from the network map onto the canvas.

        Iterates through the map's hubs, calculates their pixel
        coordinates using the scale factor, draws a colored background,
        and overlays the corresponding sprite.
        """
        offset: int = 100
        # TODO: Parcourir chaque hub
        # TODO: Calculer les coordonnees x_px et y_px
        # TODO: Afficher le sprite avec create_image
        pass
