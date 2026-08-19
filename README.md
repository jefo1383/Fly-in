*This activity has been created as part of the 42 curriculum by jfoeller.*

# Fly-in: Autonomous Drone Fleet Routing System

https://github.com/user-attachments/assets/2a2ac562-5e68-434f-beac-4b0000b70450

## Description

**Fly-in** is an autonomous drone routing simulation system developed in Python 3.13 as part of the 42 common core. The objective of the project is to navigate a fleet of drones through a dynamic network of interconnected zones (represented as a graph) from a starting hub (`start_hub`) to a destination hub (`end_hub`) in the fewest possible simulation turns.

The system enforces strict real-time movement and capacity constraints:
- **Zone Capacities (`max_drones`):** Individual zones can only host a limited number of drones simultaneously (default is 1, infinite for start and end hubs)[cite: 1, 4].
- **Link Capacities (`max_link_capacity`):** Edges connecting zones have throughput limits[cite: 1, 4].
- **Zone Types & Movement Costs:**
  - `normal`: 1 turn movement cost.
  - `priority`: 1 turn movement cost (prioritized during pathfinding).
  - `restricted`: 2 turns movement cost (drones traverse a link on turn T+1 and land on the zone at turn T+2).
  - `blocked`: Inaccessible zones.

---

## Instructions

### Prerequisites
- Python 3.10 or higher (Python 3.13 recommended)
- `uv` package manager (or standard `pip` setup)

### Environment Setup & Installation
To install project dependencies and setup the virtual environment (including Tkinter GUI bindings via Micromamba if running on 42 campus clusters):

```bash
make install
```

### Usage
Execute the main simulation by providing a path to a map configuration file via the `MAP` variable:

```bash
make run MAP=easy_01.txt
```

Run in debug mode using Python's built-in debugger (`pdb`):

```bash
make debug MAP=easy_01.txt
```

### Code Quality & Standards
The project strictly adheres to PEP 8 / `flake8` standards and is fully type-annotated, passing `mypy` static type checks without errors.

Run standard linting (`flake8` + `mypy` excluding `.venv`):
```bash
make lint
```

Run strict type checking (`mypy --strict`):
```bash
make lint-strict
```

### Cleaning
To remove cached files and build artifacts:
```bash
make clean
```

To perform a full clean (removes `.venv`, installed dependencies, and campus Micromamba environments):
```bash
make fclean
```

Reinstall the environment from scratch:
```bash
make re
```

---

## Algorithm Choices & Implementation Strategy

### Spatio-Temporal BFS (Time-Space Reservation Pathfinder)
The core pathfinding algorithm (`Pathfinder` in `pathfinding.py`) is based on a **Spatio-Temporal Breadth-First Search (BFS)** utilizing a shared reservation calendar[cite: 8]:
1. **State Definition:** States are defined as tuples of `(turn_number, current_position)`, where `current_position` can be a `Hub` or a `Link`.
2. **Shared Calendar:** A global scheduling calendar (`self.calendar[turn][location]`) tracks reserved capacity slots across time.
3. **Capacity & Collision Avoidance:** Before moving a drone into a `Hub` or `Link` at turn T, the algorithm verifies that `calendar[T][location] < location.capacity`.
4. **Multi-turn Restricted Zones:** For `restricted` zones requiring 2 turns, the pathfinder books the connecting `Link` at turn T+1 and the target `RestrictedHub` at turn T+2.
5. **Priority Heuristic:** During BFS expansion, adjacent states with `priority` zones are sorted first to favor high-throughput or preferred routes.
6. **Fleet Scheduling:** Drones are routed sequentially. Each calculated path is booked into the shared calendar, ensuring zero spatial or temporal collisions.

### OOP Architecture
- **`hub_link_models.py`:** Polymorphic hierarchy for hubs (`Hub`, `NormalHub`, `PriorityHub`, `RestrictedHub`, `BlockedHub`, `StartHub`, `EndHub`) and links (`Link`).
- **`drone_map_models.py`:** Encapsulates `Drone` state (position, route history, arrival flag) and `Map` topology.
- **`parsing.py`:** Strict input parser using `pydantic` models (`HubData`, `LinkData`) to enforce line order, unique naming, absence of spaces/dashes in zone names, and custom validation.
- **`main.py`:** Orchestrates the step-by-step turn execution and metrics collection.

---

## Visual Representation Features

The project includes an interactive graphical user interface built with **Tkinter** (`graph.py`):
- **Custom Sprites:** Distinct graphic assets for starting base, target goal, intermediate hubs, and active drone units.
- **Dynamic Grid Scaling:** Automatically adjusts canvas dimensions and hub spacing based on map complexity and node count.
- **Smooth Movement Animation:** Smoothly interpolates drone positions across frames during turn transitions (`animate_drones`), handling visual offsets when multiple drones occupy or transit near the same node.
- **Embedded Logging & Metrics Panel:** Features an integrated scrolling log window displaying real-time movement commands (`D1-hub_1 D2-hub_2`) and final performance metrics upon completion:
  - Total simulation score (turns)
  - Total path movement cost
  - Average drone movements per turn
  - Average movements per drone

---

## Example Input and Expected Output

### Example Map Input (`02_simple_fork.txt`)
```text
# Easy Level 2: Simple fork with two paths
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: path_a 2 1 [color=blue]
hub: path_b 2 -1 [color=blue]
end_hub: goal 3 0 [color=red max_drones=3]

connection: start-junction [max_link_capacity=2]
connection: junction-path_a
connection: junction-path_b
connection: path_a-goal
connection: path_b-goal
```

### Expected Terminal Output
```text
Hello from fly-in!
D1-junction D2-junction
D1-path_a D2-path_b D3-junction D4-junction
D1-goal D2-goal D3-path_a D4-path_b
D3-goal D4-goal

Score: 4 turns
Total path cost: 14 movements
Average drones moves per turn: 3.5
Average moves per drone: 3.5
```

---

## Resources & AI Usage

### References & Documentation
- [Python 3.13 Documentation](https://docs.python.org/3/)
- [Tkinter GUI Programming](https://docs.python.org/3/library/tkinter.html)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)
- [Flake8 & Mypy Static Analysis](https://mypy.readthedocs.io/)
- Graph Theory & Breadth-First Search (BFS) vs Dijkstra google search.

### AI Usage Disclosure
Artificial Intelligence (AI) tools were utilized in learning mode during development in accordance with 42 curriculum guidelines:
- **Docstrings & guidance:** AI was used to generate docstring in PEP 257 format amd guide me with 'TODO' comments without giving blocks of code.
- **Code Refactoring & Type Annotations:** AI assisted in refining Pydantic validation and resolving complex `mypy` type assignments.
- **GUI & Event Handling:** AI helped structure Tkinter animation frame rates and catch `TclError` window destruction exceptions.
- **Test Case Generation:** AI was used to generate edge-case map files to test syntax parsing errors (unsupported colors, duplicate connections, invalid drone counts).
- All AI-generated suggestions were manually reviewed, tested, and verified by the author.
