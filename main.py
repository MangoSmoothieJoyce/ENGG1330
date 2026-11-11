import math

import pygame


# The basic setting of the game

WIDTH = 800
HEIGHT = 480
#the size of each tile is 40^2 pixals
TILE_SIZE = 40 
FPS = 60
PLAYER_START = (388, 208)
PLAYER_SPEED = 120
INTERACTION_DISTANCE = 58


# Time is measured in seconds and speed in pixels per second.
SAFE_DURATION = 12.0
BARRAGE_DURATION = 8.0
BULLET_SPEED = 105.0
BULLET_LIFETIME = 5.0
SHOT_INTERVAL = 0.9
SPAWN_WARNING = 0.6
BULLET_RADIUS = 6
HIT_PROTECTION = 1.5
MAX_HITS = 3
PHYSICS_STEP = 0.02
# Treat tiny amounts of remaining time as zero to allow for floating-point rounding.
# sp
TIMER_EPSILON = 1e-9

BACKGROUND = (20, 29, 42)
PANEL = (29, 43, 60)
TEXT = (232, 240, 247)
MUTED = (157, 178, 195)
BLUE = (74, 177, 232)
GREEN = (100, 222, 167)
YELLOW = (249, 204, 109)
RED = (247, 132, 133)

SYMBOLS = ["star", "circle", "triangle", "square"]
WORKSTATION_SYMBOLS = {"A": "star", "B": "circle", "C": "triangle"}
CORRECT_SYMBOLS = ["triangle", "star", "circle"]
CABINET_CODE = "482"


WIRE_DIRECTIONS = [
    ("up", "right"),
    ("right", "down"),
    ("down", "left"),
    ("left", "up"),
]
WIRE_OFFSETS = {"up": (0, -1), "right": (1, 0),
                "down": (0, 1), "left": (-1, 0)}
WIRE_RECTS = {
    "A": pygame.Rect(290, 145, 90, 90),
    "B": pygame.Rect(290, 245, 90, 90),
    "C": pygame.Rect(390, 245, 90, 90),
    "D": pygame.Rect(390, 145, 90, 90),
}
ACTIVATE_BUTTON = pygame.Rect(290, 350, 200, 38)
CHECK_BUTTON = pygame.Rect(300, 325, 150, 40)
CLEAR_BUTTON = pygame.Rect(470, 325, 100, 40)
CLOSE_BUTTON = pygame.Rect(650, 65, 40, 32)
RESTART_BUTTON = pygame.Rect(235, 295, 150, 45)
CANCEL_BUTTON = pygame.Rect(415, 295, 150, 45)
SYMBOL_BUTTONS = [
    pygame.Rect(210 + index * 100, 215, 80, 72)
    for index in range(4)
]


# 2. Main loop: update, handle input, and draw each frame


def main():
    # Game will keep opening until the user quits.
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Engineering Lab Escape - Timed Barrage Edition")

    fonts = {
        "small": pygame.font.Font(None, 20),
        "normal": pygame.font.Font(None, 24),
        "title": pygame.font.Font(None, 30),
        "code": pygame.font.Font(None, 64),
    }
    clock = pygame.time.Clock()
    world = load_map()   # Wall and device positions
    game = reset_game()  # Player position, task progress, timers, and bullets

    while True:
        # tick() returns milliseconds. Convert to seconds for movement and timers.
        frame_seconds = clock.tick(FPS) / 1000.0

        # Use held keys to update the game, then handle individual key presses and clicks.
        held_keys = pygame.key.get_pressed()
        update_game(game, world, held_keys, frame_seconds)

        events = pygame.event.get()
        action = handle_events(game, world, events)
        if action == "quit":
            break
        if action == "restart":
            game = reset_game()

        # Draw the full frame from the current game state, then show it on screen.
        draw_game(screen, fonts, game, world)
        pygame.display.flip()

    pygame.quit()


# 3. Map, initial game state, and screen changes


def load_map():
    # This is used to create a wall
    walls = [
        # a wall goes horizontal to the right from the left up corner.
        pygame.Rect(0, 0, WIDTH, TILE_SIZE),
        # a wall goes horizontal to the right from the left down corner.
        pygame.Rect(0, HEIGHT - TILE_SIZE, WIDTH, TILE_SIZE),
        # a wall goes to below vertically from the left up corner.
        pygame.Rect(0, 0, TILE_SIZE, HEIGHT),
        # a wall goes to below vertically from the right up corner.
        pygame.Rect(WIDTH - TILE_SIZE, 0, TILE_SIZE, HEIGHT),
    ]

    objects = [
        {
            "kind": "station", "name": "A", "label": "Station A",
            "rect": pygame.Rect(100, 100, 100, 50), "color": (57, 95, 113),
        },
        {
            "kind": "station", "name": "B", "label": "Station B",
            "rect": pygame.Rect(345, 95, 100, 50), "color": (57, 95, 113),
        },
        {
            "kind": "station", "name": "C", "label": "Station C",
            "rect": pygame.Rect(590, 100, 100, 50), "color": (57, 95, 113),
        },
        {
            "kind": "computer", "name": "computer", "label": "Computer",
            "rect": pygame.Rect(100, 285, 110, 60), "color": (49, 92, 136),
        },
        {
            "kind": "cabinet", "name": "cabinet", "label": "Cabinet",
            "rect": pygame.Rect(345, 285, 100, 60), "color": (130, 99, 63),
        },
        {
            "kind": "power", "name": "power", "label": "Power",
            "rect": pygame.Rect(650, 255, 55, 60), "color": (106, 78, 136),
        },
        {
            "kind": "door", "name": "door", "label": "Exit",
            "rect": pygame.Rect(760, 200, 40, 80), "color": (130, 65, 72),
        },
    ]
    return {"walls": walls, "objects": objects}


def reset_game():
    # initialize the game
    start_x, start_y = PLAYER_START
    return {
        "player": pygame.Rect(start_x, start_y, 24, 24),
        "player_x": float(start_x),
        "player_y": float(start_y),

        "symbols_found": {},
        "computer_solved": False,
        "cabinet_open": False,
        "has_key": False,
        "power_connected": False,
        "exit_unlocked": False,
        "game_won": False,
        "game_over": False,
        "inventory": [],

        "mode": "dialog",
        "dialog_title": "Engineering Lab Escape",
        "dialog_lines": [
            f"Safe: {SAFE_DURATION:g} seconds to explore and solve tasks.",
            f"Barrage: {BARRAGE_DURATION:g} seconds to dodge. Tasks are locked.",
            "Energy bolts pass through furniture. Keep moving!",
            f"You have {MAX_HITS} HP. At 0 HP, the run ends.",
            "WASD: move    E: interact    I: inventory",
            "Press Enter or Esc to begin the first safe period.",
        ],
        "selected_symbols": [],
        "code_input": "",
        "wire_rotations": {"A": 0, "B": 1, "C": 2, "D": 3},
        "feedback": "",
        "feedback_ok": False,

        "started": False,
        "phase": "safe",
        "phase_time": SAFE_DURATION,
        "wave": 0,
        "shot_timer": 0.0,
        "shot_index": 0,
        "bullets": [],
        "hits": 0,
        "invincible_time": 0.0,
        "notice": "",
        "notice_time": 0.0,
    }


def set_feedback(game, message, success=False):
    #It is use to check the correctness of the input
    game["feedback"] = message
    game["feedback_ok"] = success


def open_interface(game, mode):
    # Update the interface
    game["mode"] = mode
    set_feedback(game, "")
    if mode == "explore":
        game["started"] = True


def show_dialog(game, title, lines):
    # to notice you
    # for example, when you get something from the lab.
    open_interface(game, "dialog")
    game["dialog_title"] = title
    game["dialog_lines"] = lines


def show_notice(game, message):
    game["notice"] = message
    game["notice_time"] = 2.5


# 4. Player movement and device interaction


def update_player(game, world, keys, dt):
    """Turn WASD input into movement over this time step."""
    if game["mode"] != "explore":
        return

    # int(True) is 1 and int(False) is 0. Opposite directions cancel each other out.
    direction_x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
    direction_y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
    if direction_x != 0 and direction_y != 0:
        # Divide both directions by the square root of 2 to keep diagonal and straight speeds equal.
        diagonal_length = math.sqrt(2)
        direction_x /= diagonal_length
        direction_y /= diagonal_length

    distance_x = direction_x * PLAYER_SPEED * dt
    distance_y = direction_y * PLAYER_SPEED * dt
    move_player(game, world, distance_x, distance_y)


def move_player(game, world, distance_x, distance_y):
    """Resolve horizontal collisions first, then vertical collisions."""
    player = game["player"]
    obstacles = world["walls"].copy()
    for device in world["objects"]:
        obstacles.append(device["rect"])

    game["player_x"] += distance_x
    player.x = round(game["player_x"])
    for obstacle in obstacles:
        if not player.colliderect(obstacle):
            continue
        if distance_x > 0:
            player.right = obstacle.left
        elif distance_x < 0:
            player.left = obstacle.right
        game["player_x"] = float(player.x)

    game["player_y"] += distance_y
    player.y = round(game["player_y"])
    for obstacle in obstacles:
        if not player.colliderect(obstacle):
            continue
        if distance_y > 0:
            player.bottom = obstacle.top
        elif distance_y < 0:
            player.top = obstacle.bottom
        game["player_y"] = float(player.y)


def closest_point_on_rect(point_x, point_y, rect):
    """Limit the point's x and y coordinates to the rectangle's bounds."""
    # Use the nearest edge if x is outside the rectangle. Otherwise, keep x.
    closest_x = min(point_x, rect.right)
    closest_x = max(rect.left, closest_x)

    # Do the same for y. In Pygame, y increases downward.
    closest_y = min(point_y, rect.bottom)
    closest_y = max(rect.top, closest_y)
    return closest_x, closest_y


def find_nearby_object(game, world):
    """Find the device closest to the player's center within interaction range."""
    player_x, player_y = game["player"].center
    nearest_device = None
    nearest_distance = INTERACTION_DISTANCE

    for device in world["objects"]:
        closest_x, closest_y = closest_point_on_rect(player_x, player_y, device["rect"])
        distance_x = player_x - closest_x
        distance_y = player_y - closest_y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if distance < nearest_distance:
            nearest_device = device
            nearest_distance = distance

    return nearest_device


def interact_object(game, obj):
    if game["game_over"] or game["game_won"]:
        return
    if game["phase"] == "barrage":
        show_notice(game, "DODGE! Tasks unlock during the next safe period.")
        return
    kind = obj["kind"]
    if kind == "station":
        name = obj["name"]
        symbol = WORKSTATION_SYMBOLS[name]
        game["symbols_found"][name] = symbol
        show_dialog(game, "Workstation " + name,
                    ["The label shows: " + symbol.upper(),
                     "This clue has been recorded in your inventory.",
                     "Close this window, then press I to review clues."])
    elif kind == "computer":
        if game["computer_solved"]:
            show_dialog(game, "Computer: verified",
                        ["Cabinet access code: " + CABINET_CODE,
                         "The cabinet keypad is now enabled."])
        else:
            open_interface(game, "symbols")
    elif kind == "cabinet":
        if game["cabinet_open"]:
            show_dialog(game, "Cabinet: open",
                        ["You already collected the Exit Control Key and note.",
                         "Use the key at the Power panel."])
        elif not game["computer_solved"]:
            show_dialog(game, "Cabinet: locked",
                        ["Keypad disabled. Complete computer verification first."])
        else:
            open_interface(game, "keypad")
    elif kind == "power":
        if not game["has_key"]:
            show_dialog(game, "Access restricted",
                        ["Control Key required. Search the locked cabinet."])
        elif game["power_connected"]:
            show_dialog(game, "Power restored",
                        ["The exit is unlocked. Go to the door and press E."])
        else:
            open_interface(game, "power")
    elif kind == "door":
        if game["exit_unlocked"]:
            game["game_won"] = True
            game["bullets"] = []
            open_interface(game, "victory")
        else:
            show_dialog(game, "Exit: locked",
                        ["The electronic lock has no power.",
                         "Restore the connection at the Power panel."])


# 5. Demo: phase changes, bullet patterns, and hits


def update_game(game, world, keys, dt):
    """Advance the game by dt, the number of seconds elapsed this frame."""
    if not game["started"] or game["game_won"] or game["game_over"]:
        return

    frame_time_left = dt
    while frame_time_left > TIMER_EPSILON:
        # Take a step of at most 0.02 seconds and stop at the end of the current phase.
        # If the frame crosses into the next phase, handle its remaining time on the next loop iteration.
        step = min(frame_time_left, PHYSICS_STEP, game["phase_time"])
        game["notice_time"] = max(0.0, game["notice_time"] - step)
        game["invincible_time"] = max(0.0, game["invincible_time"] - step)
        update_player(game, world, keys, step)

        if game["phase"] == "barrage":
            if game["shot_timer"] <= TIMER_EPSILON:
                spawn_bullets(game)
                game["shot_timer"] += SHOT_INTERVAL
            game["shot_timer"] -= step

            update_bullets(game, step)
            if game["game_over"]:
                return

        game["phase_time"] -= step
        frame_time_left -= step
        if game["phase_time"] <= TIMER_EPSILON:
            switch_phase(game)


def switch_phase(game):
    """Switch between the safe and barrage phases and update the game state."""
    if game["phase"] == "safe":
        game["phase"] = "barrage"
        game["phase_time"] = BARRAGE_DURATION
        game["wave"] += 1
        game["shot_timer"] = 0.0
        # Return to the map so the player can move immediately. Selected symbols stay in game.
        open_interface(game, "explore")
        show_notice(game, "BARRAGE! Dodge with WASD. Your task progress is kept.")
    else:
        game["phase"] = "safe"
        game["phase_time"] = SAFE_DURATION
        game["bullets"] = []
        show_notice(game, "SAFE! Use E for tasks or I to review your clues.")


def spawn_bullets(game):
    """Spawn one bullet from each of the four directions."""
    horizontal_lanes = [180, 220, 265, 370, 410, 80]
    vertical_lanes = [80, 250, 320, 470, 550, 730]
    shot_index = game["shot_index"]

    # Use % to wrap the index and cycle through the lanes in order.
    from_left_y = horizontal_lanes[shot_index % len(horizontal_lanes)]
    from_right_y = horizontal_lanes[(shot_index + 3) % len(horizontal_lanes)]
    from_top_x = vertical_lanes[(shot_index + 1) % len(vertical_lanes)]
    from_bottom_x = vertical_lanes[(shot_index + 4) % len(vertical_lanes)]

    # Each shot stores (start x, start y, x direction, y direction).
    shots = [
        (48, from_left_y, 1, 0),
        (752, from_right_y, -1, 0),
        (from_top_x, 48, 0, 1),
        (from_bottom_x, 432, 0, -1),
    ]
    for start_x, start_y, direction_x, direction_y in shots:
        bullet = {
            "x": float(start_x),
            "y": float(start_y),
            "dx": direction_x,
            "dy": direction_y,
            "warning": SPAWN_WARNING,
            "life": BULLET_LIFETIME,
        }
        game["bullets"].append(bullet)

    game["shot_index"] += 1


def update_bullets(game, dt):
    """Update warnings and movement, remove expired bullets, and check for hits."""
    if game["game_over"] or game["game_won"]:
        return

    remaining_bullets = []
    for bullet in game["bullets"]:
        # Use as much of this step as needed for the warning. Move during the time left over.
        warning_time_used = min(dt, bullet["warning"])
        bullet["warning"] = max(0.0, bullet["warning"] - warning_time_used)
        move_time = dt - warning_time_used

        bullet["life"] -= move_time
        bullet["x"] += bullet["dx"] * BULLET_SPEED * move_time
        bullet["y"] += bullet["dy"] * BULLET_SPEED * move_time

        inside_room = 40 <= bullet["x"] <= 760 and 40 <= bullet["y"] <= 440
        if bullet["life"] <= 0 or not inside_room:
            continue

        warning_finished = bullet["warning"] <= 0
        player_can_take_damage = game["invincible_time"] <= 0
        if warning_finished and player_can_take_damage:
            if bullet_hits_player(bullet, game["player"]):
                hit_player(game)
                if game["game_over"]:
                    return
                # This bullet hit the player, so leave it out of the remaining bullets.
                continue

        remaining_bullets.append(bullet)

    game["bullets"] = remaining_bullets


def bullet_hits_player(bullet, player):
    """Count a hit if the circle's center is within one radius of the nearest point on the rectangle."""
    bullet_x = bullet["x"]
    bullet_y = bullet["y"]
    closest_x, closest_y = closest_point_on_rect(bullet_x, bullet_y, player)

    distance_x = bullet_x - closest_x
    distance_y = bullet_y - closest_y
    distance_squared = distance_x ** 2 + distance_y ** 2
    radius_squared = BULLET_RADIUS ** 2
    return distance_squared <= radius_squared


def hit_player(game):
    """Record a hit. If the player has health left, return them to the start and grant brief protection."""
    if game["game_over"] or game["game_won"] or game["invincible_time"] > 0:
        return
    game["hits"] += 1
    if game["hits"] >= MAX_HITS:
        game["game_over"] = True
        game["bullets"] = []
        game["invincible_time"] = 0.0
        game["notice_time"] = 0.0
        open_interface(game, "game_over")
        return
    start_x, start_y = PLAYER_START
    game["player"].topleft = PLAYER_START
    game["player_x"] = float(start_x)
    game["player_y"] = float(start_y)
    game["invincible_time"] = HIT_PROTECTION
    health = MAX_HITS - game["hits"]
    show_notice(game, f"HIT! {health} HP left. Back at start; brief shield on. Progress kept.")


# 6. Puzzle validation rules


def check_symbol_sequence(game):
    if len(game["selected_symbols"]) != 3:
        set_feedback(game, "Choose exactly three symbols first.")
    elif game["selected_symbols"] == CORRECT_SYMBOLS:
        game["computer_solved"] = True
        set_feedback(game, "Verified! Cabinet code: 482. Press Esc to return.", True)
    else:
        game["selected_symbols"] = []
        set_feedback(game, "Incorrect sequence. Please try again.")


def check_cabinet_code(game):
    if game["code_input"] != CABINET_CODE:
        game["code_input"] = ""
        set_feedback(game, "Access denied. Incorrect code. Try again.")
        return
    game["cabinet_open"] = True
    game["has_key"] = True
    game["inventory"] = ["Exit Control Key", "Power Connection Note"]
    show_dialog(game, "Cabinet unlocked",
                ["Collected: Exit Control Key + Power Connection Note.",
                 "NOTE: Restore power from the generator to the exit.",
                 "Rotate the wires to form a continuous connection.",
                 "Go to the Power panel near the exit."])


def check_power_connection(game):
    """Check both ends of each wire tile along the path from the generator through A, B, C, and D to the exit."""
    required_connections = {
        "A": ("left", "down"),
        "B": ("up", "right"),
        "C": ("left", "up"),
        "D": ("down", "right"),
    }

    wires = {}
    for name, rotation in game["wire_rotations"].items():
        wires[name] = WIRE_DIRECTIONS[rotation]

    for name, (first_end, second_end) in required_connections.items():
        if first_end not in wires[name] or second_end not in wires[name]:
            return False
    return True


def activate_power(game):
    if check_power_connection(game):
        game["power_connected"] = True
        game["exit_unlocked"] = True
        set_feedback(game, "Power restored! Exit unlocked. Press Esc.", True)
    else:
        set_feedback(game, "Connection failed. Rotate the tiles and try again.")


# 7. Keyboard and mouse input


def handle_events(game, world, events):
    """Handle clicks and key presses in order. A key can have a different effect on each screen."""
    for event in events:
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            action = handle_click(game, event.pos)
            if action is not None:
                return action
        if event.type != pygame.KEYDOWN:
            continue

        mode = game["mode"]
        if event.key == pygame.K_ESCAPE:
            if mode in ("victory", "game_over"):
                return "quit"
            open_interface(game, "explore")
        elif mode == "explore":
            if event.key == pygame.K_e:
                obj = find_nearby_object(game, world)
                if obj is not None:
                    interact_object(game, obj)
            elif event.key == pygame.K_i:
                if game["phase"] == "safe":
                    open_interface(game, "inventory")
                else:
                    show_notice(game, "Keep dodging. Inventory opens during the safe period.")
            elif event.key == pygame.K_r:
                if game["phase"] == "safe":
                    open_interface(game, "restart")
                else:
                    show_notice(game, "Keep dodging. Restart is available during the safe period.")
        elif mode == "dialog" and event.key == pygame.K_RETURN:
            open_interface(game, "explore")
        elif mode == "inventory" and event.key == pygame.K_i:
            open_interface(game, "explore")
        elif mode == "keypad":
            if event.key == pygame.K_BACKSPACE:
                game["code_input"] = game["code_input"][:-1]
                set_feedback(game, "")
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                check_cabinet_code(game)
            else:
                typed_character = event.unicode
                if typed_character and typed_character in "0123456789":
                    if len(game["code_input"]) < 3:
                        game["code_input"] += typed_character
                        set_feedback(game, "")
        elif mode == "symbols" and not game["computer_solved"]:
            if event.key == pygame.K_RETURN:
                check_symbol_sequence(game)
            elif event.key == pygame.K_BACKSPACE:
                game["selected_symbols"] = game["selected_symbols"][:-1]
                set_feedback(game, "")
        elif mode == "power" and event.key == pygame.K_RETURN:
            if not game["power_connected"]:
                activate_power(game)
        elif mode == "restart" and event.key == pygame.K_RETURN:
            return "restart"
        elif mode in ("victory", "game_over") and event.key in (pygame.K_r, pygame.K_RETURN):
            return "restart"
    return None


def handle_click(game, position):
    mode = game["mode"]
    if mode not in ("explore", "victory", "game_over") and CLOSE_BUTTON.collidepoint(position):
        open_interface(game, "explore")
        return None
    if mode == "symbols" and not game["computer_solved"]:
        for index, rect in enumerate(SYMBOL_BUTTONS):
            if rect.collidepoint(position) and len(game["selected_symbols"]) < 3:
                game["selected_symbols"].append(SYMBOLS[index])
                set_feedback(game, "")
        if CHECK_BUTTON.collidepoint(position):
            check_symbol_sequence(game)
        elif CLEAR_BUTTON.collidepoint(position):
            game["selected_symbols"] = []
            set_feedback(game, "")
    elif mode == "power" and not game["power_connected"]:
        for name, rect in WIRE_RECTS.items():
            if rect.collidepoint(position):
                # Each click rotates the tile 90 degrees. The index wraps from 3 to 0.
                current_rotation = game["wire_rotations"][name]
                game["wire_rotations"][name] = (current_rotation + 1) % 4
                set_feedback(game, "")
        if ACTIVATE_BUTTON.collidepoint(position):
            activate_power(game)
    elif mode in ("restart", "victory", "game_over"):
        if RESTART_BUTTON.collidepoint(position):
            return "restart"
        if CANCEL_BUTTON.collidepoint(position):
            if mode in ("victory", "game_over"):
                return "quit"
            open_interface(game, "explore")
    return None


# 8. Draw the current game state


def draw_game(screen, fonts, game, world):
    draw_map(screen, fonts, game, world)
    mode = game["mode"]
    if mode == "explore":
        draw_phase_hud(screen, fonts, game)
        return
    titles = {"dialog": game["dialog_title"], "symbols": "Computer Verification",
              "keypad": "Cabinet Access", "power": "Power Connection",
              "inventory": "Inventory & Clues", "restart": "Restart game?",
              "victory": "Laboratory Escape Complete", "game_over": "Game Over"}
    draw_window(screen, fonts, titles[mode], closable=mode not in ("victory", "game_over"))
    if mode == "dialog":
        for index, line in enumerate(game["dialog_lines"]):
            draw_text(screen, fonts, line, 130, 135 + index * 39)
        if game["dialog_title"].startswith("Workstation "):
            name = game["dialog_title"][-1]
            draw_symbol(screen, WORKSTATION_SYMBOLS[name], (400, 330), 30)
    elif mode == "symbols":
        draw_text(screen, fonts, "Enter symbols in this order: C -> A -> B", 130, 120)
        for i, symbol in enumerate(game["selected_symbols"]):
            draw_symbol(screen, symbol, (330 + i * 70, 178), 16)
        for symbol, rect in zip(SYMBOLS, SYMBOL_BUTTONS):
            pygame.draw.rect(screen, (47, 66, 86), rect, border_radius=7)
            draw_symbol(screen, symbol, rect.center)
        draw_text(screen, fonts, "Click three symbols. Backspace removes the last one.",
                  160, 299, MUTED, "small")
        draw_button(screen, fonts, CHECK_BUTTON, "Check / Enter")
        draw_button(screen, fonts, CLEAR_BUTTON, "Clear", MUTED)
    elif mode == "keypad":
        draw_text(screen, fonts, "Enter the three-digit code from the computer.", 130, 130)
        displayed_code = game["code_input"].ljust(3, "_")
        draw_text(screen, fonts, "  ".join(displayed_code), 400, 225,
                  YELLOW, "code", True)
        draw_text(screen, fonts, "0-9: type    Backspace: delete    Enter: confirm",
                  400, 305, MUTED, "small", True)
    elif mode == "power":
        draw_power_puzzle(screen, fonts, game)
    elif mode == "inventory":
        draw_inventory(screen, fonts, game)
    elif mode in ("restart", "victory", "game_over"):
        if mode == "victory":
            draw_text(screen, fonts, "Congratulations! You escaped the laboratory.",
                      400, 172, GREEN, center=True)
            draw_text(screen, fonts, "Both puzzles solved. All systems restored.",
                      400, 215, MUTED, center=True)
        elif mode == "game_over":
            draw_text(screen, fonts, f"You were hit {MAX_HITS} times. No HP remaining.",
                      400, 165, RED, center=True)
            draw_text(screen, fonts, "Restart for a fresh attempt with full HP.",
                      400, 207, TEXT, center=True)
            draw_text(screen, fonts, "R / Enter: restart    Esc: quit",
                      400, 247, MUTED, "small", True)
        else:
            draw_text(screen, fonts, "Restarting clears all progress in this session.",
                      400, 175, center=True)
            draw_text(screen, fonts, "Press Enter to restart, or Esc to cancel.",
                      400, 215, MUTED, center=True)
        draw_button(screen, fonts, RESTART_BUTTON, "Restart")
        draw_button(screen, fonts, CANCEL_BUTTON,
                    "Quit" if mode in ("victory", "game_over") else "Cancel", MUTED)
    if game["feedback"]:
        color = GREEN if game["feedback_ok"] else RED
        draw_text(screen, fonts, game["feedback"], 125, 389, color, "small")
    draw_phase_hud(screen, fonts, game)


def draw_map(screen, fonts, game, world):
    screen.fill(BACKGROUND)
    for row in range(12):
        for column in range(20):
            tile = pygame.Rect(column * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (28, 39, 53), tile, 1)
    for wall in world["walls"]:
        pygame.draw.rect(screen, (44, 57, 74), wall)

    can_interact = game["mode"] == "explore" and game["phase"] == "safe"
    nearby = find_nearby_object(game, world) if can_interact else None
    for obj in world["objects"]:
        color = obj["color"]
        if obj["kind"] == "door" and game["exit_unlocked"]:
            color = (44, 127, 96)
        if obj["kind"] == "cabinet" and game["cabinet_open"]:
            color = (70, 117, 94)
        pygame.draw.rect(screen, color, obj["rect"], border_radius=5)
        if obj is nearby:
            pygame.draw.rect(screen, YELLOW, obj["rect"].inflate(6, 6), 2, border_radius=5)
        draw_text(screen, fonts, obj["label"], *obj["rect"].center,
                  size="small", center=True)
        if obj["kind"] == "station" and obj["name"] in game["symbols_found"]:
            draw_symbol(screen, WORKSTATION_SYMBOLS[obj["name"]],
                        (obj["rect"].centerx, obj["rect"].top - 16), 9, GREEN)

    draw_bullets(screen, game)
    player_color = BLUE
    if game["invincible_time"] > 0:
        player_color = TEXT if int(game["invincible_time"] * 10) % 2 else BLUE
        pygame.draw.circle(screen, BLUE, game["player"].center, 21, 2)
    pygame.draw.rect(screen, player_color, game["player"], border_radius=6)
    pygame.draw.circle(screen, TEXT, (game["player"].centerx, game["player"].y + 7), 4)
    message = current_objective(game)
    if game["phase"] == "barrage":
        message = "WASD: dodge    Tasks locked    Energy bolts pass through furniture."
    if game["notice_time"] > 0:
        message = game["notice"]
    draw_text(screen, fonts, message, 22, 453, size="small")
    if nearby is not None:
        prompt = "E: " + nearby["label"]
        px = max(100, min(700, game["player"].centerx))
        py = max(62, game["player"].top - 22)
        label_rect = pygame.Rect(px - 98, py - 13, 196, 26)
        pygame.draw.rect(screen, PANEL, label_rect, border_radius=5)
        draw_text(screen, fonts, prompt, px, py, YELLOW, "small", True)


def draw_bullets(screen, game):
    for bullet in game["bullets"]:
        x, y = round(bullet["x"]), round(bullet["y"])
        dx, dy = bullet["dx"], bullet["dy"]
        if bullet["warning"] > 0:
            pygame.draw.circle(screen, YELLOW, (x, y), 10, 2)
            pygame.draw.line(screen, YELLOW, (x, y), (x + dx * 18, y + dy * 18), 2)
        else:
            pygame.draw.line(screen, RED, (x - dx * 15, y - dy * 15), (x, y), 3)
            pygame.draw.circle(screen, RED, (x, y), BULLET_RADIUS)
            pygame.draw.circle(screen, TEXT, (x + dx * 2, y + dy * 2), 2)


def draw_phase_hud(screen, fonts, game):
    danger = game["phase"] == "barrage"
    warning = not danger and game["phase_time"] <= 3
    color = RED if danger else (YELLOW if warning else GREEN)
    label = "DODGE / TASKS LOCKED" if danger else "SAFE / DO TASKS"
    if warning:
        label = "BARRAGE INCOMING"
    if not game["started"]:
        label = "READY / READ INSTRUCTIONS"
    if game["game_won"]:
        label = "ESCAPED / TIMER STOPPED"
        color = GREEN
    elif game["game_over"]:
        label = "GAME OVER / TIMER STOPPED"
        color = RED
    pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 40))
    seconds = f'{game["phase_time"]:.1f}s'
    draw_text(screen, fonts, label, 16, 8, color, "small")
    draw_text(screen, fonts, seconds, 278, 7, color)
    health = max(0, MAX_HITS - game["hits"])
    health_color = RED if health <= 1 else TEXT
    draw_text(screen, fonts, f'Wave {game["wave"]}   HP {health}/{MAX_HITS}',
              365, 8, health_color, "small")
    draw_text(screen, fonts, "WASD Move   E Task   I Bag   R Restart", 535, 8, MUTED, "small")
    duration = BARRAGE_DURATION if danger else SAFE_DURATION
    bar_width = round(WIDTH * max(0, min(1, game["phase_time"] / duration)))
    pygame.draw.rect(screen, color, (0, 34, bar_width, 6))
    if danger:
        pygame.draw.rect(screen, RED, (40, 40, 720, 400), 2)
    elif warning and int(game["phase_time"] * 4) % 2:
        pygame.draw.rect(screen, YELLOW, (40, 40, 720, 400), 2)


def draw_window(screen, fonts, title, closable=True):
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 175))
    screen.blit(shade, (0, 0))
    pygame.draw.rect(screen, PANEL, (100, 50, 600, 380), border_radius=12)
    pygame.draw.rect(screen, (65, 88, 110), (100, 50, 600, 380), 2, border_radius=12)
    draw_text(screen, fonts, title, 125, 71, size="title")
    if closable:
        draw_button(screen, fonts, CLOSE_BUTTON, "X", MUTED)
    draw_text(screen, fonts, "Esc: close" if closable else "R: restart    Esc: quit",
              125, 405, MUTED, "small")


def draw_inventory(screen, fonts, game):
    draw_text(screen, fonts, "RECORDED CLUES", 130, 122, BLUE)
    for index, name in enumerate(["A", "B", "C"]):
        x = 180 + index * 185
        draw_text(screen, fonts, "Station " + name, x, 163, center=True)
        if name in game["symbols_found"]:
            draw_symbol(screen, game["symbols_found"][name], (x, 199), 17)
        else:
            draw_text(screen, fonts, "?", x, 199, MUTED, center=True)
    code = CABINET_CODE if game["computer_solved"] else "not discovered"
    draw_text(screen, fonts, "Cabinet code: " + code, 130, 242)
    items = ", ".join(game["inventory"]) if game["inventory"] else "None yet"
    draw_text(screen, fonts, "Items: " + items, 130, 277, size="small")
    if game["has_key"]:
        draw_text(screen, fonts, "NOTE: Rotate wires to connect generator to exit.",
                  130, 317, YELLOW, "small")
        draw_text(screen, fonts, "Items are used automatically; no need to equip them.",
                  130, 348, MUTED, "small")


def draw_power_puzzle(screen, fonts, game):
    draw_text(screen, fonts, "Click a tile to rotate it 90 degrees clockwise.", 130, 113, size="small")
    wire_color = GREEN if game["power_connected"] else YELLOW

    for start, end in [((235, 190), (290, 190)), ((480, 190), (535, 190)),
                       ((335, 235), (335, 245)), ((380, 290), (390, 290)),
                       ((435, 235), (435, 245))]:
        pygame.draw.line(screen, wire_color, start, end, 6)
    draw_text(screen, fonts, "GENERATOR", 215, 167, GREEN, "small", True)
    draw_text(screen, fonts, "EXIT", 555, 167, GREEN, "small", True)
    for name, rect in WIRE_RECTS.items():
        pygame.draw.rect(screen, (47, 66, 86), rect, border_radius=7)
        pygame.draw.rect(screen, (87, 111, 131), rect, 1, border_radius=7)
        cx, cy = rect.center
        directions = WIRE_DIRECTIONS[game["wire_rotations"][name]]
        for direction in directions:
            dx, dy = WIRE_OFFSETS[direction]
            pygame.draw.line(screen, wire_color, (cx, cy), (cx + dx * 45, cy + dy * 45), 7)
        pygame.draw.circle(screen, wire_color, (cx, cy), 6)
        draw_text(screen, fonts, name, rect.x + 7, rect.y + 5, TEXT, "small")
    draw_button(screen, fonts, ACTIVATE_BUTTON,
                "Power Restored" if game["power_connected"] else "Activate Power",
                GREEN if game["power_connected"] else BLUE)


def current_objective(game):
    if game["exit_unlocked"]:
        return "Exit unlocked: go to the door and press E."
    if game["has_key"]:
        return "Use the Power panel to restore the exit connection."
    if game["computer_solved"]:
        return "Open the cabinet. Your access code is saved in inventory."
    return "Inspect stations A, B and C, then use the computer."


def draw_text(screen, fonts, text, x, y, color=TEXT, size="normal", center=False):
    image = fonts[size].render(text, True, color)
    rect = image.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(image, rect)


def draw_button(screen, fonts, rect, label, color=BLUE):
    pygame.draw.rect(screen, color, rect, border_radius=7)
    draw_text(screen, fonts, label, *rect.center, color=BACKGROUND, center=True)


def draw_symbol(screen, symbol, center, radius=18, color=YELLOW):
    x, y = center
    if symbol == "circle":
        pygame.draw.circle(screen, color, center, radius)
    elif symbol == "square":
        pygame.draw.rect(screen, color, (x - radius, y - radius, radius * 2, radius * 2))
    elif symbol == "triangle":
        pygame.draw.polygon(screen, color, [(x, y - radius),
                            (x - radius, y + radius), (x + radius, y + radius)])
    elif symbol == "star":
        points = []
        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5
            length = radius if i % 2 == 0 else radius * 0.45
            points.append((x + math.cos(angle) * length, y + math.sin(angle) * length))
        pygame.draw.polygon(screen, color, points)


if __name__ == "__main__":
    main()
