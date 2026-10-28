# ENGG1330
ENGG1330 group project (group 5)

## Project
Engineering Lab Escape

## Members
- Junhyuk Jang
- Ming Yu Ye
- Yebin Lee

## Description
A console adventure game where the player solves connected puzzles to escape an engineering lab.

## Game Story
The player is locked inside an engineering laboratory and must solve a series of connected puzzles to escape.

The player first finds a computer containing a puzzle. Solving it reveals a code for a locked cabinet. Inside the cabinet, the player finds a clue needed for the second puzzle. Solving the second puzzle allows the player to unlock the final exit and escape the laboratory.

## Game Flow
Start
→ Explore the engineering lab
→ Computer Puzzle
→ Receive cabinet code
→ Open cabinet
→ Find clue
→ Second Puzzle
→ Unlock exit
→ Escape

# Engineering Lab Escape
## Game Logic & Mechanics Design Document

**Game Type:** 2D Top-Down Exploration & Puzzle Adventure

**Development Environment:** Python + Pygame

**Players:** Single-player

**Estimated Playtime:** 5–10 minutes

**Target Audience:** General players with no prior engineering knowledge

---

## 1. Game Overview

Engineering Lab Escape is a 2D puzzle adventure game in which the player wakes up inside a locked engineering laboratory following an emergency security lockdown.

The main objective is to escape by exploring the laboratory, interacting with objects, discovering clues, and solving two interconnected puzzles.

The game takes place in a single laboratory containing computers, workstations, storage cabinets, and an electronically controlled exit.

The puzzles focus on observation, pattern recognition, and logical thinking. No prior knowledge of engineering or electronics is required.

## 2. Player Controls

| Input | Action |
|---|---|
| W / A / S / D | Move up, left, down, right |
| E | Interact with nearby objects |
| Left Mouse Button | Select symbols, buttons, and rotate puzzle tiles |
| Number Keys | Enter cabinet access code |
| Backspace | Delete a digit |
| Enter | Confirm code |
| Esc | Close the current interface |

### Movement Mechanics

The player moves freely in four directions within the laboratory.

The game uses collision detection to prevent movement through walls, laboratory furniture, and locked doors.

When the player approaches an interactive object, a visual prompt appears:

"Press E to interact"

Pressing E opens the appropriate interaction interface.

Player movement is temporarily disabled while a puzzle or dialogue window is open.

## 3. Laboratory Map Design

The laboratory is designed as a single fixed 2D tile-based environment.

Initial map specifications:

- Map dimensions: 20 × 12 tiles
- Tile size: 40 × 40 pixels
- Window resolution: 800 × 480 pixels
- Camera: Fixed top-down view
- Player movement: 120 pixels per second

### Interactive Objects

| Object | Purpose |
|---|---|
| Workstation A | Displays the Star symbol |
| Workstation B | Displays the Circle symbol |
| Workstation C | Displays the Triangle symbol |
| Computer Terminal | Controls Puzzle 1 |
| Locked Cabinet | Contains a key and instructions |
| Exit Control Panel | Controls Puzzle 2 |
| Exit Door | Final escape destination |

All interactive objects have fixed positions. Players are encouraged to explore the laboratory to discover the information needed for each puzzle.

## 4. Puzzle 1 — Symbol Sequence

**Objective:** Discover three symbols and enter them in the correct order to obtain the cabinet access code.

### Step 1: Explore the Laboratory

The player can investigate three workstations.

Each workstation displays a different symbol:

- Workstation A: ★ (Star)
- Workstation B: ● (Circle)
- Workstation C: ▲ (Triangle)

When the player approaches a workstation and presses E, the corresponding symbol is displayed.

The game records which workstations have been inspected.

### Step 2: Interact with the Computer

When the player interacts with the main computer, a puzzle interface appears.

The computer displays the following instruction:

"Security Verification Required. Enter the symbols in this order: C → A → B."

Below the instruction, four clickable symbol buttons are displayed: ★, ●, ▲ and ■.

The player must select three symbols in the correct order.

**Correct Answer:** ▲ → ★ → ●

### Step 3: Validate the Answer

The game compares the player's selected symbol sequence with the correct sequence.

If the answer is incorrect:

- A message appears: "Incorrect sequence. Please try again."
- The selected sequence is cleared.
- The player may retry without penalty.

If the answer is correct:

- The computer displays: "Verification Successful."
- The cabinet access code, **482**, is revealed.
- The computer authorizes the cabinet keypad.
- Puzzle 1 is marked as completed.

## 5. Cabinet Unlocking

The cabinet is initially locked, and its keypad is disabled until the computer verification has been completed.

After completing Puzzle 1, the player can approach the cabinet and press E to open a three-digit keypad interface.

The player enters the code revealed by the computer.

**Correct Code:** 482

If the code is incorrect, the cabinet remains locked and the game displays:

"Access Denied. Incorrect Code."

If the code is correct:

- The cabinet opens permanently.
- The player automatically receives an Exit Control Key.
- The player also receives a note explaining the second puzzle.

The note reads:

"Restore the power connection from the generator to the exit door. Rotate the wire pieces until a continuous path is formed."

The obtained key and note are stored in the player's inventory.

## 6. Puzzle 2 — Power Connection

**Objective:** Restore power to the laboratory exit by completing a visual wire-connection puzzle.

The player approaches the exit control panel and presses E.

If the player does not have the Exit Control Key, the panel displays:

"Access Restricted. Control Key Required."

If the player has the key, the power connection puzzle opens.

### Puzzle Interface

The puzzle consists of four rotatable L-shaped wire tiles arranged in a 2 × 2 grid.

| A | D |
|---|---|
| B | C |

The generator is connected to the left side of tile A. The exit is connected to the right side of tile D.

Each wire tile has two connection directions. Clicking a tile rotates it 90 degrees clockwise.

### Correct Connection Path

The intended connection must follow this path:

Generator → A → B → C → D → Exit

The correct orientations are:

| Tile | Required Connections |
|---|---|
| A (Top-left) | Left and Down |
| B (Bottom-left) | Up and Right |
| C (Bottom-right) | Left and Up |
| D (Top-right) | Down and Right |

The initial tile orientations are different from the solution, so the player must rotate them.

### Answer Validation

The player clicks an "Activate Power" button after arranging the wires.

The game checks whether all four wire tiles connect correctly along the required path.

If the connections are incorrect:

- The system displays: "Power Connection Failed."
- The current wire orientations remain unchanged.
- The player can continue rotating tiles and try again.

If all connections are correct:

- The connected wires turn green.
- The system displays: "Power Restored. Exit Unlocked."
- Puzzle 2 is marked as completed.
- The laboratory exit door unlocks.

There is no time limit or maximum number of attempts.

## 7. Game Progression

The intended gameplay sequence is:

**Stage 1 — Exploration**

The player enters the laboratory and investigates nearby objects.

**Stage 2 — Symbol Discovery**

The player discovers the symbols displayed at workstations A, B, and C.

**Stage 3 — Computer Puzzle**

The player enters the correct symbol sequence and obtains the cabinet code.

**Stage 4 — Cabinet Unlocking**

The player unlocks the cabinet and collects the Exit Control Key and instructions.

**Stage 5 — Power Connection Puzzle**

The player uses the key to access the control panel and restores power.

**Stage 6 — Escape**

After unlocking the exit, the player approaches the door and presses E.

The game displays:

"Congratulations! You have successfully escaped the Engineering Laboratory!"

The game then transitions to a victory screen with an option to restart or quit.

## 8. Game State Management

The game must track the following variables:

| Variable | Initial Value | Updated When |
|---|---|---|
| `symbols_found` | Empty collection | A workstation is inspected |
| `computer_solved` | False | Symbol sequence is correct |
| `cabinet_open` | False | Correct cabinet code is entered |
| `has_key` | False | Cabinet contents are collected |
| `power_connected` | False | Wire puzzle is completed |
| `exit_unlocked` | False | Power is restored |
| `game_won` | False | Player interacts with the unlocked exit |

These variables determine which interactions and actions are available.

For example, the control panel is accessible only when `has_key == True`.

The player can win only when the exit has been unlocked.

## 9. Additional Game Mechanics

### Interaction System

Interactive objects respond only when the player is within a short interaction distance.

When several objects are nearby, the game prioritizes the closest object.

### Inventory System

The inventory stores collected items and discovered clues.

The player can review obtained information without returning to the original object.

For this initial version, inventory items are collected automatically and do not need to be manually equipped.

### Puzzle Retry System

Players have unlimited attempts to solve both puzzles.

Incorrect answers provide feedback without resetting previous progress.

### Progress Saving

Game progress is stored in memory during the current session.

Permanent saving and loading are outside the scope of the initial version.

### Restart System

The player can restart the game from the beginning. Restarting resets all puzzle states, collected items, and the player's position.

## 10. Game Completion Conditions

The game is successfully completed when all of the following conditions are satisfied:

1. The computer puzzle has been solved.
2. The cabinet has been unlocked.
3. The Exit Control Key has been collected.
4. The power connection puzzle has been solved.
5. The player interacts with the unlocked exit door.

The game contains no combat, health system, or game-over penalty.

The primary challenge comes from exploration and puzzle-solving.

## 11. Development Scope

The initial playable version will include:

- One complete 2D laboratory map
- One controllable player character
- Four-directional movement
- Wall and object collision detection
- Interactive laboratory objects
- A basic inventory system
- One symbol sequence puzzle
- One wire connection puzzle
- A locked cabinet and an exit door
- A victory screen

Additional rooms, random puzzles, animations, sound effects, and advanced inventory mechanics may be considered after the core game has been completed.
