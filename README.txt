Engineering Lab Escape - Ready-to-Use Map and Playable Demo

SPECIFICATIONS
20 columns x 12 rows; 40 x 40 pixels per tile; 800 x 480 window.
Fixed top-down 2D map.
Based on the MangoSmoothieJoyce/ENGG1330 README, checked on November 3, 2026.

SETUP AND RUN
Requires Python 3.10 or later.
Open a terminal in the extracted Engineering_Lab_Map folder and run:
  python3 -m pip install -r requirements.txt
  python3 engineering_lab_map.py
On Windows, use python instead of python3 if python3 is not recognized.

CONTROLS
W / A / S / D: Move.
E: Interact with the nearest object within reach.
I: Review discovered clues and collected items.
Left mouse button: Select symbols and rotate wire tiles.
Number keys: Enter the cabinet access code.
Backspace: Delete a digit.
Enter: Confirm the code.
Esc: Close the current panel.
Close the game window to quit. The victory screen offers Restart and Quit.
Progress is kept only for the current session and is not saved to disk.

FILES
engineering_lab_map.py: Standalone playable demo; also importable into a project.
engineering_lab_map.png: Map preview with labels and HUD. Do not use it directly
as a collision map.
lab_map.json: Tile layout, object positions, and legend. Coordinates are
zero-based (column, row), with x increasing rightward and y downward.
requirements.txt: Pygame dependency.
README.txt: Setup, controls, integration instructions, and developer walkthrough.

MAP OBJECTS AND POSITIONS
Coordinates below use zero-based (column, row).
P  Player spawn        (2, 9)
A  Workstation A       (3, 3)
B  Workstation B       (5, 7)
C  Workstation C       (12, 3)
T  Computer terminal   (6, 2)
K  Locked cabinet      (16, 3)
X  Exit control panel  (16, 8)
D  Exit door           (19, 8)
The central dividing wall has an upper and a lower passage, allowing players
to explore both sides and return to previously visited objects.

INTEGRATING THE MAP INTO AN EXISTING main.py
  from engineering_lab_map import load_map, draw_map, move_player, find_nearby_object, fonts
  lab = load_map()
  player_center = lab.spawn
After initializing Pygame and the fonts, use draw_map to render the scene,
move_player to update the player position, and find_nearby_object to retrieve
the nearby object ID. Connect those IDs to your own puzzle interfaces.
The Game class provides a complete interaction demo. It is optional if you
only need the map.
Collision uses full 40-pixel tiles. Decorative gaps around furniture sprites
are not walkable.

DEVELOPER WALKTHROUGH - CONTAINS SOLUTIONS
1. Inspect the workstations: A shows a Star, B a Circle, and C a Triangle.
2. At the computer, select the symbols in C / A / B order:
   Triangle, Star, Circle.
3. Receive the cabinet code: 482.
4. Enter 482 at the cabinet to collect the Exit Control Key and instructions.
5. At the exit control panel, rotate the four wire tiles to restore power.
6. Approach the exit door and press E to escape.

Wire layout: A at top-left, D at top-right, B at bottom-left, C at bottom-right.
Required connections:
A: Left and Down.
B: Up and Right.
C: Left and Up.
D: Down and Right.
Incorrect answers can be retried. There is no countdown or health system.

VALIDATION
Rendering and simulated input checks were completed with Pygame 2.6.1 using
a headless display driver.
All 158 floor tiles are connected, and all 7 interactive objects are reachable.
Checks passed for collision, progression locks, incorrect-answer retries,
the complete escape sequence, restart, and movement being paused while a
panel is open.
The demo has not been run on your Mac. Install Pygame before the first run.
