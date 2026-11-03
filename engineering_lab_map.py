"""ENGG1330 Group 5 — fixed map and playable walkthrough for Engineering Lab Escape.

Run: python3 -m pip install pygame
     python3 engineering_lab_map.py

The map can also be imported into main.py. Call load_map() once, use
lab.spawn for the player center, and use draw_map(), move_player(), and
find_nearby_object() in the game loop. Object IDs are A, B, C, T, K, X, D.
"""
from dataclasses import dataclass, field
from math import cos, pi, sin

import pygame


TILE_SIZE = 40
WIDTH, HEIGHT = 800, 480
PLAYER_SIZE = 22
PLAYER_SPEED = 120
INTERACT_DISTANCE = 49

# # wall, . floor, = furniture, P spawn; all other characters are objects.
MAP_LAYOUT = (
    "####################",
    "#........#.........#",
    "#.....T..#.........#",
    "#.=A=....#.=C=..K..#",
    "#..................#",
    "#........#.........#",
    "#........#...===...#",
    "#...=B=..#.........#",
    "#........#......X..D",
    "#.P................#",
    "#..................#",
    "####################",
)

NAVY = "#101b2b"
PANEL = "#17283b"
TEXT = "#edf5ff"
MUTED = "#9bb4cc"
CYAN = "#65e0f2"
YELLOW = "#ffd68d"
GREEN = "#84e4ab"
CORAL = "#ff9d98"

OBJECTS = {
    "A": ("Workstation A", "A / WORKSTATION", CYAN),
    "B": ("Workstation B", "B / WORKSTATION", CYAN),
    "C": ("Workstation C", "C / WORKSTATION", CYAN),
    "T": ("Computer Terminal", "01 / TERMINAL", CYAN),
    "K": ("Locked Cabinet", "02 / CABINET", YELLOW),
    "X": ("Exit Control Panel", "03 / CONTROL", YELLOW),
    "D": ("Exit Door", "04 / EXIT", CORAL),
}
SYMBOLS = {"A": "Star", "B": "Circle", "C": "Triangle"}
CABINET_CODE = "482"
CABINET_NOTE = "Restore the power connection from the generator to the exit door."
DIRECTIONS = ((0, -1), (1, 0), (0, 1), (-1, 0))  # up, right, down, left
WIRE_SOLUTIONS = (2, 1, 0, 3)  # row-major A, D / B, C; first arm of each L
WIRE_START = (0, 3, 2, 1)


@dataclass
class LabMap:
    tiles: tuple
    walls: list
    furniture: list
    objects: dict
    spawn: tuple


def load_map():
    """Return the tile grid, collision geometry, object rectangles and spawn center."""
    walls, furniture, objects = [], [], {}
    spawn = None
    for row, tiles in enumerate(MAP_LAYOUT):
        for col, tile in enumerate(tiles):
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if tile == "#":
                walls.append(rect)
            elif tile == "=":
                furniture.append(rect)
            elif tile == "P":
                spawn = rect.center
            elif tile in OBJECTS:
                objects[tile] = rect
    return LabMap(MAP_LAYOUT, walls, furniture, objects, spawn)


def solid_rects(lab, exit_unlocked=False):
    """The exit is solid while locked. Its tile stays within the screen bounds."""
    return lab.walls + lab.furniture + [
        rect for key, rect in lab.objects.items() if key != "D" or not exit_unlocked
    ]


def player_rect(center):
    rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
    rect.center = (round(center[0]), round(center[1]))
    return rect


def check_collision(lab, center, exit_unlocked=False):
    rect = player_rect(center)
    return not pygame.Rect(0, 0, WIDTH, HEIGHT).contains(rect) or (
        rect.collidelist(solid_rects(lab, exit_unlocked)) != -1
    )


def move_player(lab, center, direction, dt, exit_unlocked=False):
    """Move on one axis at a time so the player slides along a wall."""
    motion = pygame.Vector2(direction)
    position = pygame.Vector2(center)
    if not motion:
        return position
    motion.scale_to_length(PLAYER_SPEED * min(dt, 0.05))
    for axis in (0, 1):
        candidate = position.copy()
        candidate[axis] += motion[axis]
        if not check_collision(lab, candidate, exit_unlocked):
            position = candidate
    return position


def find_nearby_object(lab, center):
    """Return the closest reachable object ID, or None."""
    position = pygame.Vector2(center)
    blockers = solid_rects(lab)
    for key, rect in sorted(lab.objects.items(), key=lambda item: position.distance_to(item[1].center)):
        if position.distance_to(rect.center) > INTERACT_DISTANCE:
            return None
        if not any(
            other is not rect and other.clipline(position, rect.center)
            for other in blockers
        ):
            return key
    return None


def label(surface, font, message, position, color=TEXT, *, center=False):
    ink = font.render(message, True, color)
    rect = ink.get_rect(center=position) if center else ink.get_rect(topleft=position)
    surface.blit(ink, rect)


def fonts():
    return {
        "tiny": pygame.font.Font(None, 15),
        "small": pygame.font.Font(None, 19),
        "body": pygame.font.Font(None, 24),
        "title": pygame.font.Font(None, 36),
    }


def draw_symbol(surface, symbol, center, size, color):
    x, y = center
    if symbol == "Circle":
        pygame.draw.circle(surface, color, center, size)
    elif symbol == "Square":
        pygame.draw.rect(surface, color, (x - size, y - size, 2 * size, 2 * size))
    elif symbol == "Triangle":
        pygame.draw.polygon(surface, color, [(x, y - size), (x - size, y + size), (x + size, y + size)])
    elif symbol == "Star":
        points = []
        for index in range(10):
            angle = index * pi / 5 - pi / 2
            radius = size if index % 2 == 0 else size * 0.44
            points.append((x + radius * cos(angle), y + radius * sin(angle)))
        pygame.draw.polygon(surface, color, points)


def draw_object(surface, key, rect, accent):
    """Draw the fixed furniture and a different icon for each device type."""
    box = rect.inflate(-4, -4)
    if key == "D":
        pygame.draw.rect(surface, "#253449", rect)
        pygame.draw.rect(surface, accent, (rect.x + 8, rect.y + 4, 24, 32), 2, border_radius=3)
        pygame.draw.line(surface, accent, (rect.centerx, rect.y + 8), (rect.centerx, rect.bottom - 8))
        return
    pygame.draw.rect(surface, "#0b1522", box.move(0, 3), border_radius=5)
    pygame.draw.rect(surface, "#263b51", box, border_radius=5)
    pygame.draw.rect(surface, "#4b657d", box, 1, border_radius=5)
    x, y = rect.center
    if key in SYMBOLS or key == "T":
        pygame.draw.rect(surface, "#102031", (x - 11, y - 10, 22, 15), border_radius=2)
        pygame.draw.rect(surface, accent, (x - 11, y - 10, 22, 15), 1, border_radius=2)
        pygame.draw.line(surface, accent, (x - 6, y + 9), (x + 6, y + 9))
        if key == "T":
            pygame.draw.lines(surface, accent, False, [(x - 6, y - 6), (x - 3, y - 3), (x - 6, y)], 2)
            pygame.draw.line(surface, accent, (x, y), (x + 5, y))
        else:
            pygame.draw.circle(surface, accent, (x, y - 3), 2)
    elif key == "K":
        pygame.draw.rect(surface, accent, (x - 9, y - 11, 18, 22), 1, border_radius=3)
        pygame.draw.line(surface, accent, (x - 9, y - 1), (x + 9, y - 1))
        pygame.draw.line(surface, accent, (x - 2, y + 5), (x + 3, y + 5), 2)
    else:
        pygame.draw.lines(surface, accent, False, [(x + 2, y - 10), (x - 6, y + 1),
                                                  (x + 5, y + 1), (x - 2, y + 10)], 2)


def draw_map(surface, lab, typefaces, *, center=None, nearby=None, exit_unlocked=False):
    """Render the fixed 800×480 scene. Pass center to show the player."""
    surface.fill(NAVY)
    for row, tiles in enumerate(lab.tiles):
        for col, tile in enumerate(tiles):
            if tile == "#":
                continue
            tile_rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            floor = "#182d40" if col < 9 else "#1b3245"
            pygame.draw.rect(surface, floor, tile_rect)
            pygame.draw.rect(surface, "#233e52", tile_rect, 1)

    for rect in lab.walls:
        pygame.draw.rect(surface, "#253548", rect)
        pygame.draw.rect(surface, "#34485d", rect, 1)
        pygame.draw.line(surface, "#41576d", (rect.left + 3, rect.top + 4),
                         (rect.right - 4, rect.top + 4))

    for rect in lab.furniture:
        body = rect.inflate(-4, -8)
        pygame.draw.rect(surface, "#0c1825", body.move(0, 4), border_radius=4)
        pygame.draw.rect(surface, "#344c61", body, border_radius=4)
        pygame.draw.rect(surface, "#587087", body, 1, border_radius=4)
        pygame.draw.line(surface, "#6b8598", (body.left + 5, body.top + 6),
                         (body.right - 6, body.top + 6))

    for message, position in (
        ("WEST  /  RESEARCH BENCHES", (53, 54)),
        ("EAST  /  EQUIPMENT & STORAGE", (415, 54)),
        ("CROSS AISLE", (370, 412)),
    ):
        label(surface, typefaces["tiny"], message, position, MUTED)

    for key, rect in lab.objects.items():
        _, caption, accent = OBJECTS[key]
        if key == "D" and exit_unlocked:
            accent = GREEN
        draw_object(surface, key, rect, accent)
        caption_x = min(rect.centerx, 738)
        caption_y = rect.top - 8 if key in ("T", "C", "K", "D") else rect.bottom + 9
        label(surface, typefaces["tiny"], caption, (caption_x, caption_y), accent, center=True)
        if key == nearby:
            pygame.draw.rect(surface, accent, rect.inflate(4, 4), 2, border_radius=6)

    pygame.draw.circle(surface, "#38596e", lab.spawn, 15, 1)
    label(surface, typefaces["tiny"], "SPAWN", (lab.spawn[0], lab.spawn[1] + 22), MUTED, center=True)
    if center is not None:
        point = (round(center[0]), round(center[1]))
        pygame.draw.circle(surface, "#102031", point, 13)
        pygame.draw.circle(surface, CYAN, point, 9)
        pygame.draw.circle(surface, TEXT, (point[0] - 2, point[1] - 2), 3)

    pygame.draw.rect(surface, NAVY, (0, 0, WIDTH, TILE_SIZE))
    pygame.draw.line(surface, "#4c697f", (0, 39), (WIDTH, 39))
    label(surface, typefaces["body"], "ENGINEERING LAB ESCAPE", (18, 10))
    label(surface, typefaces["small"], "ENGG1330   /   GROUP 05", (597, 13), CYAN)

    pygame.draw.rect(surface, NAVY, (0, HEIGHT - TILE_SIZE, WIDTH, TILE_SIZE))
    pygame.draw.line(surface, "#4c697f", (0, HEIGHT - TILE_SIZE), (WIDTH, HEIGHT - TILE_SIZE))
    label(surface, typefaces["small"], "WASD  Move    E  Interact    I  Inventory", (18, 453), MUTED)
    prompt = f"Press E  /  {OBJECTS[nearby][0]}" if nearby else "EXIT UNLOCKED" if exit_unlocked else "EXIT LOCKED"
    label(surface, typefaces["small"], prompt, (615, 460), GREEN if exit_unlocked else YELLOW, center=True)


@dataclass
class GameState:
    symbols_found: set = field(default_factory=set)
    computer_solved: bool = False
    cabinet_open: bool = False
    has_key: bool = False
    power_connected: bool = False
    exit_unlocked: bool = False
    game_won: bool = False


SYMBOL_CHOICES = ("Star", "Circle", "Triangle", "Square")
SYMBOL_BUTTONS = [pygame.Rect(185 + i * 113, 215, 93, 65) for i in range(4)]
WIRE_BUTTONS = [pygame.Rect(327 + i % 2 * 74, 182 + i // 2 * 74, 72, 72) for i in range(4)]
ACTIVATE_BUTTON = pygame.Rect(301, 343, 198, 35)
RESTART_BUTTON = pygame.Rect(248, 296, 145, 38)
QUIT_BUTTON = pygame.Rect(407, 296, 145, 38)
CLOSE_BUTTON = pygame.Rect(631, 71, 34, 28)


class Game:
    """A small walkthrough that exercises the map using the README puzzle rules."""

    def __init__(self, lab, typefaces):
        self.lab = lab
        self.fonts = typefaces
        self.reset()

    def reset(self):
        self.state = GameState()
        self.center = pygame.Vector2(self.lab.spawn)
        self.mode = None
        self.title = ""
        self.lines = ()
        self.feedback = ""
        self.selected = []
        self.code = ""
        self.wires = list(WIRE_START)

    def open(self, mode, title="", *lines):
        self.mode = mode
        self.title = title
        self.lines = lines
        self.feedback = ""

    def interact_object(self, key):
        state = self.state
        if key in SYMBOLS:
            state.symbols_found.add(key)
            self.open("message", OBJECTS[key][0], f"Inspected symbol: {SYMBOLS[key]}.")
        elif key == "T":
            if state.computer_solved:
                self.open("message", "Computer Terminal", f"Verification successful. Cabinet code: {CABINET_CODE}.")
            else:
                self.selected.clear()
                self.open("symbols", "Security Verification")
        elif key == "K":
            if state.cabinet_open:
                self.show_note()
            elif state.computer_solved:
                self.code = ""
                self.open("keypad", "Cabinet Keypad")
            else:
                self.open("message", "Cabinet Locked", "Complete the computer verification to enable the keypad.")
        elif key == "X":
            if state.power_connected:
                self.open("message", "Power Restored", "The exit door is unlocked. Approach it and press E.")
            elif state.has_key:
                self.open("wires", "Restore Exit Power")
            else:
                self.open("message", "Access Restricted", "Control Key Required.")
        elif key == "D":
            if state.exit_unlocked:
                state.game_won = True
                self.open("victory", "Laboratory Escaped")
            else:
                self.open("message", "Exit Locked", "Restore power at the exit control panel.")

    def show_note(self):
        self.open("message", "Cabinet Open", "Exit Control Key collected.", CABINET_NOTE,
                  "Rotate the wire pieces until a continuous path is formed.")

    def show_inventory(self):
        clues = [f"{key}: {SYMBOLS[key]}" for key in SYMBOLS if key in self.state.symbols_found]
        lines = ["Workstations   " + ("  /  ".join(clues) if clues else "None inspected")]
        if self.state.computer_solved:
            lines.append(f"Cabinet code   {CABINET_CODE}")
        if self.state.has_key:
            lines += ["Item   Exit Control Key", CABINET_NOTE,
                      "Rotate the wire pieces until a continuous path is formed."]
        self.open("message", "Inventory", *lines)

    def choose_symbol(self, symbol):
        self.selected.append(symbol)
        if len(self.selected) == 3:
            if self.selected == [SYMBOLS[key] for key in "CAB"]:
                self.state.computer_solved = True
                self.open("message", "Verification Successful", f"Cabinet access code: {CABINET_CODE}.",
                          "The cabinet keypad is now enabled.")
            else:
                self.selected.clear()
                self.feedback = "Incorrect sequence. Please try again."

    def handle_event(self, event):
        """Return False when the player chooses to quit."""
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if self.mode == "victory":
                if event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    return False
            elif self.mode:
                if event.key == pygame.K_ESCAPE:
                    self.open(None)
                elif self.mode == "keypad":
                    self.handle_keypad(event)
            elif event.key == pygame.K_e:
                self.interact_object(find_nearby_object(self.lab, self.center))
            elif event.key == pygame.K_i:
                self.show_inventory()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.handle_click(event.pos)
        return True

    def handle_keypad(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.code = self.code[:-1]
            self.feedback = ""
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.code == CABINET_CODE:
                self.state.cabinet_open = self.state.has_key = True
                self.show_note()
            else:
                self.code = ""
                self.feedback = "Access Denied. Incorrect Code."
        elif event.unicode in "0123456789" and event.unicode and len(self.code) < 3:
            self.code += event.unicode
            self.feedback = ""

    def handle_click(self, point):
        if self.mode == "victory":
            if RESTART_BUTTON.collidepoint(point):
                self.reset()
            return not QUIT_BUTTON.collidepoint(point)
        if self.mode and CLOSE_BUTTON.collidepoint(point):
            self.open(None)
        elif self.mode == "symbols":
            for button, symbol in zip(SYMBOL_BUTTONS, SYMBOL_CHOICES):
                if button.collidepoint(point):
                    self.feedback = ""
                    self.choose_symbol(symbol)
                    break
        elif self.mode == "wires":
            for index, button in enumerate(WIRE_BUTTONS):
                if button.collidepoint(point):
                    self.wires[index] = (self.wires[index] + 1) % 4
                    self.feedback = ""
                    break
            if ACTIVATE_BUTTON.collidepoint(point):
                if tuple(self.wires) == WIRE_SOLUTIONS:
                    self.state.power_connected = self.state.exit_unlocked = True
                    self.mode = "powered"
                    self.feedback = "Power Restored. Exit Unlocked."
                else:
                    self.feedback = "Power Connection Failed."
        return True

    def update(self, keys, dt):
        if not self.mode:
            direction = (keys[pygame.K_d] - keys[pygame.K_a], keys[pygame.K_s] - keys[pygame.K_w])
            self.center = move_player(self.lab, self.center, direction, dt, self.state.exit_unlocked)

    def draw(self, surface):
        draw_map(surface, self.lab, self.fonts, center=self.center,
                 nearby=find_nearby_object(self.lab, self.center), exit_unlocked=self.state.exit_unlocked)
        if not self.mode:
            return

        tiny, small, body, title = (self.fonts[key] for key in ("tiny", "small", "body", "title"))
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((5, 12, 23, 180))
        surface.blit(veil, (0, 0))
        frame = pygame.Rect(124, 63, 552, 355)
        pygame.draw.rect(surface, PANEL, frame, border_radius=11)
        pygame.draw.rect(surface, "#4b657d", frame, 1, border_radius=11)
        label(surface, tiny, "LAB SECURITY SYSTEM", (150, 86), CYAN)
        label(surface, title, self.title, (149, 112))

        if self.mode != "victory":
            draw_button(surface, small, CLOSE_BUTTON, "X", MUTED)
            label(surface, small, "Esc  Close", (150, 392), MUTED)
        if self.mode == "message":
            for index, line in enumerate(self.lines):
                label(surface, body, line, (150, 174 + index * 28))
        elif self.mode == "symbols":
            label(surface, body, "Enter the workstation symbols in order: C  >  A  >  B.", (150, 172))
            for button, symbol in zip(SYMBOL_BUTTONS, SYMBOL_CHOICES):
                draw_button(surface, small, button, "")
                draw_symbol(surface, symbol, (button.centerx, button.centery - 6), 11, CYAN)
                label(surface, small, symbol, (button.centerx, button.bottom - 12), MUTED, center=True)
            sequence = "  >  ".join(self.selected) if self.selected else "Choose three symbols."
            label(surface, body, sequence, (400, 314), TEXT, center=True)
        elif self.mode == "keypad":
            label(surface, body, "Enter the three-digit cabinet access code.", (150, 173))
            for index in range(3):
                slot = pygame.Rect(303 + index * 67, 218, 60, 65)
                digit = self.code[index:index + 1] or "_"
                draw_button(surface, title, slot, digit)
            label(surface, small, "Number keys  /  Backspace  /  Enter", (400, 314), MUTED, center=True)
        elif self.mode in ("wires", "powered"):
            color = GREEN if self.mode == "powered" else CYAN
            label(surface, small, "Rotate each wire to connect the generator to the exit.", (150, 153))
            for tile, rotation, name in zip(WIRE_BUTTONS, self.wires, "ADBC"):
                draw_button(surface, small, tile, "", color)
                label(surface, tiny, name, (tile.x + 7, tile.y + 7), MUTED)
                for arm in (rotation, (rotation + 1) % 4):
                    dx, dy = DIRECTIONS[arm]
                    end = (tile.centerx + dx * 36, tile.centery + dy * 36)
                    pygame.draw.line(surface, color, tile.center, end, 5)
                pygame.draw.circle(surface, color, tile.center, 4)
            y = WIRE_BUTTONS[0].centery
            pygame.draw.line(surface, color, (292, y), (327, y), 5)
            pygame.draw.line(surface, color, (473, y), (508, y), 5)
            label(surface, small, "GENERATOR", (240, y), MUTED, center=True)
            label(surface, small, "EXIT", (537, y), MUTED, center=True)
            if self.mode == "wires":
                draw_button(surface, body, ACTIVATE_BUTTON, "Activate Power")
        elif self.mode == "victory":
            label(surface, body, "You successfully escaped the Engineering Laboratory!", (150, 182))
            draw_button(surface, body, RESTART_BUTTON, "Restart")
            draw_button(surface, body, QUIT_BUTTON, "Quit", MUTED)

        if self.feedback:
            y = 388 if self.mode == "wires" else 360
            label(surface, body, self.feedback, (400, y),
                  GREEN if self.mode == "powered" else CORAL, center=True)


def draw_button(surface, font, rect, caption, color=CYAN):
    pygame.draw.rect(surface, "#21384d", rect, border_radius=6)
    pygame.draw.rect(surface, "#4b657d", rect, 1, border_radius=6)
    if caption:
        label(surface, font, caption, rect.center, color, center=True)


def main():
    pygame.init()
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Engineering Lab Escape | ENGG1330")
        clock = pygame.time.Clock()
        game = Game(load_map(), fonts())
        running = True
        while running:
            dt = clock.tick(60) / 1000
            for event in pygame.event.get():
                if not game.handle_event(event):
                    running = False
                    break
            if running:
                game.update(pygame.key.get_pressed(), dt)
                game.draw(screen)
                pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
