import math
import random
import pygame



width = 800
height = 480
tilesize = 40 
fps = 60
playerstart = (388, 208)
playerspeed = 120
interactiondistance = 58


safeduration = 12.0
barrageduration = 8.0
bulletspeed = 105.0
bulletlifetime = 5.0
shotinterval = 0.9
spawnwarning = 0.6
bulletradius = 6
hitprotection = 1.5
maxhits = 3
physicsstep = 0.02
timerepsilon = 1e-9

background = (20, 29, 42)
panel = (29, 43, 60)
text = (232, 240, 247)
muted = (157, 178, 195)
blue = (74, 177, 232)
green = (100, 222, 167)
yellow = (249, 204, 109)
red = (247, 132, 133)

symbols = ["star", "circle", "triangle", "square"]

chosensymbols = random.sample(symbols, 3)

workstationsymbols = {}
workstationsymbols["A"] = chosensymbols[0]
workstationsymbols["B"] = chosensymbols[1]
workstationsymbols["C"] = chosensymbols[2]

correctsymbols = []
correctsymbols.append(workstationsymbols["C"])
correctsymbols.append(workstationsymbols["A"])
correctsymbols.append(workstationsymbols["B"])

codenumber = random.randint(100, 999)
cabinetcode = str(codenumber)


wiredirections = [
    ("up", "right"),
    ("right", "down"),
    ("down", "left"),
    ("left", "up"),
]
wireoffsets = {"up": (0, -1), "right": (1, 0),
                "down": (0, 1), "left": (-1, 0)}
wirerects = {
    "A": pygame.Rect(290, 145, 90, 90),
    "B": pygame.Rect(290, 245, 90, 90),
    "C": pygame.Rect(390, 245, 90, 90),
    "D": pygame.Rect(390, 145, 90, 90),
}
activatebutton = pygame.Rect(290, 350, 200, 38)
checkbutton = pygame.Rect(300, 325, 150, 40)
clearbutton = pygame.Rect(470, 325, 100, 40)
closebutton = pygame.Rect(650, 65, 40, 32)
restartbutton = pygame.Rect(235, 295, 150, 45)
cancelbutton = pygame.Rect(415, 295, 150, 45)
symbolbuttons = []
for index in range(4):
    x = 210 + index * 100
    buttonrect = pygame.Rect(x, 215, 80, 72)
    symbolbuttons.append(buttonrect)


def closest_point_on_rect(point_x, point_y, rect):
    if point_x < rect.left:
        closest_x = rect.left
    elif point_x > rect.right:
        closest_x = rect.right
    else:
        closest_x = point_x

    if point_y < rect.top:
        closest_y = rect.top
    elif point_y > rect.bottom:
        closest_y = rect.bottom
    else:
        closest_y = point_y

    return closest_x, closest_y


class Game:
    def __init__(self):
        # Player doesn't have a constructor, so it doesn't need "self" for parameter.
        self.player = Player()
        # Those objects are belonged to Game, but they are referencing to other, so that attributes from those objects could share.
        self.barrage = Barrage(self)
        self.puzzle = Puzzle(self)
        self.input_handler = InputHandler(self)
        self.renderer = Renderer(self)

    # initialize the game
    def main(self):
        pygame.init()
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Engineering Lab Escape - Timed Barrage Edition")

        fonts = {
            "small": pygame.font.Font(None, 20),
            "normal": pygame.font.Font(None, 24),
            "title": pygame.font.Font(None, 30),
            "code": pygame.font.Font(None, 64),
        }
        clock = pygame.time.Clock()
        world = self.load_map()
        game = self.reset_game()
        
        # keep the game running until the player quits
        while True:
            frame_seconds = clock.tick(fps) / 1000.0

            # Use held keys to update the game, then handle individual key presses and clicks.
            held_keys = pygame.key.get_pressed()
            self.update_game(game, world, held_keys, frame_seconds)

            events = pygame.event.get()
            action = self.input_handler.handle_events(game, world, events)
            if action == "quit":
                break
            if action == "restart":
                game = self.reset_game()

            # Draw the full frame from the current game state, then show it on screen.
            self.renderer.draw_game(screen, fonts, game, world)
            pygame.display.flip()

        pygame.quit()

    def load_map(self):
        walls = [
            pygame.Rect(0, 0, width, tilesize),
            pygame.Rect(0, height - tilesize, width, tilesize),
            pygame.Rect(0, 0, tilesize, height),
            pygame.Rect(width - tilesize, 0, tilesize, height),
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

    # reset all value if player failed the game
    def reset_game(self):
        start_x, start_y = playerstart
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
                f"Safe: {safeduration:g} seconds to explore and solve tasks.",
                f"Barrage: {barrageduration:g} seconds to dodge. Tasks are locked.",
                "Energy bolts pass through furniture. Keep moving!",
                f"You have {maxhits} HP. At 0 HP, the run ends.",
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
            "phase_time": safeduration,
            "wave": 0,
            "shot_timer": 0.0,
            "shot_index": 0,
            "bullets": [],
            "hits": 0,
            "invincible_time": 0.0,
            "notice": "",
            "notice_time": 0.0,
        }

    # show the result when player iteracted with something. For example, if player's input is correct, shows green, otherwise shows red.
    def set_feedback(self, game, message, success=False):
        game["feedback"] = message
        game["feedback_ok"] = success

    # change the interface screen if needs and will also reset the old feedback.
    def open_interface(self, game, mode):
        game["mode"] = mode
        self.set_feedback(game, "")
        if mode == "explore":
            game["started"] = True

    # show information
    def show_dialog(self, game, title, lines):
        self.open_interface(game, "dialog")
        game["dialog_title"] = title
        game["dialog_lines"] = lines

    # when event is coming, this method will notice the player.
    # For example, before barrage time started, it will notice "barrage will come! Please avoid them"
    def show_notice(self, game, message):
        game["notice"] = message
        game["notice_time"] = 2.5

    def interact_object(self, game, obj):
        # End the game when player failed or won.
        if game["game_over"] or game["game_won"]:
            return
        # lock tasks during the barrage phase and notice the player.
        if game["phase"] == "barrage":
            message = "DODGE! Tasks unlock during the next safe period."
            self.show_notice(game, message)
            return

        kind = obj["kind"]
        #the interaction with station
        if kind == "station":
            name = obj["name"]
            symbol = workstationsymbols[name]

            found_symbols = game["symbols_found"]
            found_symbols[name] = symbol

            title = "Workstation " + name
            lines = [
                "The label shows: " + symbol.upper(),
                "This clue has been recorded in your inventory.",
                "Close this window, then press I to review clues.",
            ]
            self.show_dialog(game, title, lines)
            return
        #the interaction with computer
        if kind == "computer":
            #check if player completed the task on lab-computer
            if game["computer_solved"]:
                lines = [
                    "Cabinet access code: " + cabinetcode,
                    "The cabinet keypad is now enabled.",
                ]
                self.show_dialog(game, "Computer: verified", lines)
                return

            self.open_interface(game, "symbols")
            return
        #the interaction with cabinet
        if kind == "cabinet":
            # player cannot get anything from the canbinet if they have already finished the task at here.
            if game["cabinet_open"]:
                lines = [
                    "You already collected the Exit Control Key and note.",
                    "Use the key at the Power panel.",
                ]
                self.show_dialog(game, "Cabinet: open", lines)
                return
            # player must finish the task on lab-computer first.
            if not game["computer_solved"]:
                lines = ["Keypad disabled. Complete computer verification first."]
                self.show_dialog(game, "Cabinet: locked", lines)
                return

            self.open_interface(game, "keypad")
            return

        # player is forbidden to interact with the power station if they don't have the key from cabinet.
        if kind == "power":
            if not game["has_key"]:
                lines = ["Control Key required. Search the locked cabinet."]
                self.show_dialog(game, "Access restricted", lines)
                return
            # if the power station already has power, player cannot power the station again.
            if game["power_connected"]:
                lines = ["The exit is unlocked. Go to the door and press E."]
                self.show_dialog(game, "Power restored", lines)
                return

            self.open_interface(game, "power")
            return
        #Player win the game if the door is unlocked and he or she left the lab.
        if kind == "door":
            if game["exit_unlocked"]:
                game["game_won"] = True
                game["bullets"] = []
                self.open_interface(game, "victory")
                return

            lines = [
                "The electronic lock has no power.",
                "Restore the connection at the Power panel.",
            ]
            self.show_dialog(game, "Exit: locked", lines)

    #This method don't need to return anything when the game is not running.
    def update_game(self, game, world, keys, dt):
        if not game["started"] or game["game_won"] or game["game_over"]:
            return

        frame_time_left = dt
        # Using frame rate and time to determine game performance
        while frame_time_left > timerepsilon:
            step = frame_time_left

            if step > physicsstep:
                step = physicsstep

            if step > game["phase_time"]:
                step = game["phase_time"]

            game["notice_time"] -= step
            if game["notice_time"] < 0:
                game["notice_time"] = 0.0

            game["invincible_time"] -= step
            if game["invincible_time"] < 0:
                game["invincible_time"] = 0.0

            self.player.update_player(game, world, keys, step)

            if game["phase"] == "barrage":
                if game["shot_timer"] <= timerepsilon:
                    self.barrage.spawn_bullets(game)
                    game["shot_timer"] += shotinterval

                game["shot_timer"] -= step
                self.barrage.update_bullets(game, step)

                if game["game_over"]:
                    return

            game["phase_time"] -= step
            frame_time_left -= step

            if game["phase_time"] <= timerepsilon:
                self.switch_phase(game)

    # two different game phases give different interface and notice.
    def switch_phase(self, game):
        if game["phase"] == "safe":
            game["phase"] = "barrage"
            game["phase_time"] = barrageduration
            game["wave"] += 1
            game["shot_timer"] = 0.0
            self.open_interface(game, "explore")
            self.show_notice(game, "BARRAGE! Dodge with WASD. Your task progress is kept.")
        else:
            game["phase"] = "safe"
            game["phase_time"] = safeduration
            game["bullets"] = []
            self.show_notice(game, "SAFE! Use E for tasks or I to review your clues.")


class Player:
    def update_player(self, game, world, keys, dt):
        # player can only move if they are not doing the task.
        if game["mode"] != "explore":
            return

        direction_x = 0
        direction_y = 0

        #keyboard controll
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction_x = direction_x + 1
    
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction_x = direction_x - 1
    
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction_y = direction_y + 1
    
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction_y = direction_y - 1
        if direction_x != 0 and direction_y != 0:
            diagonal_length = math.sqrt(2)
            direction_x /= diagonal_length
            direction_y /= diagonal_length

        distance_x = direction_x * playerspeed * dt
        distance_y = direction_y * playerspeed * dt
        self.move_player(game, world, distance_x, distance_y)

    def move_player(self, game, world, distance_x, distance_y):
        player = game["player"]
        # add all obstacles in lab into the list including computer, canbinet, power station, etc.
        obstacles = world["walls"].copy()
        for device in world["objects"]:
            obstacles.append(device["rect"])

        game["player_x"] += distance_x
        player.x = round(game["player_x"])
        for obstacle in obstacles:
            if not player.colliderect(obstacle):
                continue
            # if player is moving to the right, its right side is the left side of the obstacle.
            if distance_x > 0:
                player.right = obstacle.left
            # if player is moving to the left, its right side is the right side of the obstacle.
            elif distance_x < 0:
                player.left = obstacle.right
            game["player_x"] = float(player.x)

        game["player_y"] += distance_y
        player.y = round(game["player_y"])
        for obstacle in obstacles:
            if not player.colliderect(obstacle):
                continue
            if distance_y > 0:
                # if player is moving down, its below is the above of the obstacle.
                player.bottom = obstacle.top
            elif distance_y < 0:
                # if player is moving up, its below is the below of the obstacle.
                player.top = obstacle.bottom
            game["player_y"] = float(player.y)

    def find_nearby_object(self, game, world):
        player_x, player_y = game["player"].center
        nearest_device = None
        nearest_distance = interactiondistance

        # it is used to calculate which thing nearest to the player
        for device in world["objects"]:
            device_rect = device["rect"]
            closest_point = closest_point_on_rect(player_x, player_y, device_rect)
            closest_x = closest_point[0]
            closest_y = closest_point[1]
            distance_x = player_x - closest_x
            distance_y = player_y - closest_y
            distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

            if distance < nearest_distance:
                nearest_device = device
                nearest_distance = distance

        return nearest_device


class Barrage:
    def __init__(self, controller):
        self.controller = controller

    def spawn_bullets(self, game):
        horizontal_lanes = [180, 220, 265, 370, 410, 80]
        vertical_lanes = [80, 250, 320, 470, 550, 730]
        shot_index = game["shot_index"]

        horizontal_count = len(horizontal_lanes)
        vertical_count = len(vertical_lanes)
    
        left_index = shot_index % horizontal_count
        right_index = (shot_index + 3) % horizontal_count
        top_index = (shot_index + 1) % vertical_count
        bottom_index = (shot_index + 4) % vertical_count
    
        from_left_y = horizontal_lanes[left_index]
        from_right_y = horizontal_lanes[right_index]
        from_top_x = vertical_lanes[top_index]
        from_bottom_x = vertical_lanes[bottom_index]
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
                "warning": spawnwarning,
                "life": bulletlifetime,
            }
            game["bullets"].append(bullet)

        game["shot_index"] += 1

    def update_bullets(self, game, dt):
        if game["game_over"] or game["game_won"]:
            return

        remaining_bullets = []
        for bullet in game["bullets"]:
            warning_time_used = dt

            #bullet will start to move after the warning
            if bullet["warning"] < warning_time_used:
                warning_time_used = bullet["warning"]
            # if the moving time is 0.04, warning time is 0.02, the actual moving time will be 0.04s - 0.02s
            bullet["warning"] = bullet["warning"] - warning_time_used
            if bullet["warning"] < 0:
                bullet["warning"] = 0.0
            move_time = dt - warning_time_used

            bullet["life"] -= move_time
            bullet["x"] += bullet["dx"] * bulletspeed * move_time
            bullet["y"] += bullet["dy"] * bulletspeed * move_time

            inside_room = 40 <= bullet["x"] <= 760 and 40 <= bullet["y"] <= 440
            #if the bullet is outside from the map or its duration less than 0, the method will not handle it anymore.
            if bullet["life"] <= 0 or not inside_room:
                continue

            warning_finished = False
            if bullet["warning"] <= 0:
                warning_finished = True

            # the interaction between bullet and player
            player_can_take_damage = False
            if game["invincible_time"] <= 0:
                player_can_take_damage = True
            if warning_finished and player_can_take_damage:
                if self.bullet_hits_player(bullet, game["player"]):
                    self.hit_player(game)
                    if game["game_over"]:
                        return
                    continue

            remaining_bullets.append(bullet)

        game["bullets"] = remaining_bullets

    def bullet_hits_player(self, bullet, player):
        bullet_x = bullet["x"]
        bullet_y = bullet["y"]
        closest_x, closest_y = closest_point_on_rect(bullet_x, bullet_y, player)

        distance_x = bullet_x - closest_x
        distance_y = bullet_y - closest_y
        distance_squared = distance_x ** 2 + distance_y ** 2
        radius_squared = bulletradius ** 2
        return distance_squared <= radius_squared

    def hit_player(self, game):
        if game["game_over"] or game["game_won"] or game["invincible_time"] > 0:
            return
        game["hits"] += 1
        if game["hits"] >= maxhits:
            game["game_over"] = True
            game["bullets"] = []
            game["invincible_time"] = 0.0
            game["notice_time"] = 0.0
            self.controller.open_interface(game, "game_over")
            return
        start_x, start_y = playerstart
        game["player"].topleft = playerstart
        game["player_x"] = float(start_x)
        game["player_y"] = float(start_y)
        game["invincible_time"] = hitprotection
        health = maxhits - game["hits"]
        self.controller.show_notice(game, f"HIT! {health} HP left. Back at start; brief shield on. Progress kept.")


class Puzzle:
    def __init__(self, controller):
        self.controller = controller

    def check_symbol_sequence(self, game):
        if len(game["selected_symbols"]) != 3:
            self.controller.set_feedback(game, "Choose exactly three symbols first.")
        elif game["selected_symbols"] == correctsymbols:
            game["computer_solved"] = True
            self.controller.set_feedback(game, "Verified! Cabinet code: 482. Press Esc to return.", True)
        else:
            game["selected_symbols"] = []
            self.controller.set_feedback(game, "Incorrect sequence. Please try again.")

    def check_cabinet_code(self, game):
        if game["code_input"] != cabinetcode:
            game["code_input"] = ""
            self.controller.set_feedback(game, "Access denied. Incorrect code. Try again.")
            return
        game["cabinet_open"] = True
        game["has_key"] = True
        game["inventory"] = ["Exit Control Key", "Power Connection Note"]
        self.controller.show_dialog(game, "Cabinet unlocked",
                    ["Collected: Exit Control Key + Power Connection Note.",
                     "NOTE: Restore power from the generator to the exit.",
                     "Rotate the wires to form a continuous connection.",
                     "Go to the Power panel near the exit."])

    def check_power_connection(self, game):
        required_connections = {
            "A": ("left", "down"),
            "B": ("up", "right"),
            "C": ("left", "up"),
            "D": ("down", "right"),
        }

        wires = {}
        for name, rotation in game["wire_rotations"].items():
            wires[name] = wiredirections[rotation]

        for name, (first_end, second_end) in required_connections.items():
            if first_end not in wires[name] or second_end not in wires[name]:
                return False
        return True

    def activate_power(self, game):
        if self.check_power_connection(game):
            game["power_connected"] = True
            game["exit_unlocked"] = True
            self.controller.set_feedback(game, "Power restored! Exit unlocked. Press Esc.", True)
        else:
            self.controller.set_feedback(game, "Connection failed. Rotate the tiles and try again.")

    def current_objective(self, game):
        if game["exit_unlocked"]:
            return "Exit unlocked: go to the door and press E."
        if game["has_key"]:
            return "Use the Power panel to restore the exit connection."
        if game["computer_solved"]:
            return "Open the cabinet. Your access code is saved in inventory."
        return "Inspect stations A, B and C, then use the computer."


# 7. Keyboard and mouse input
class InputHandler:
    def __init__(self, controller):
        self.controller = controller

    def handle_events(self, game, world, events):
        """Handle clicks and key presses in order. A key can have a different effect on each screen."""
        for event in events:
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = self.handle_click(game, event.pos)
                if action is not None:
                    return action
            if event.type != pygame.KEYDOWN:
                continue

            mode = game["mode"]
            if event.key == pygame.K_ESCAPE:
                if mode in ("victory", "game_over"):
                    return "quit"
                self.controller.open_interface(game, "explore")
            elif mode == "explore":
                if event.key == pygame.K_e:
                    obj = self.controller.player.find_nearby_object(game, world)
                    if obj is not None:
                        self.controller.interact_object(game, obj)
                elif event.key == pygame.K_i:
                    if game["phase"] == "safe":
                        self.controller.open_interface(game, "inventory")
                    else:
                        self.controller.show_notice(game, "Keep dodging. Inventory opens during the safe period.")
                elif event.key == pygame.K_r:
                    if game["phase"] == "safe":
                        self.controller.open_interface(game, "restart")
                    else:
                        self.controller.show_notice(game, "Keep dodging. Restart is available during the safe period.")
            elif mode == "dialog" and event.key == pygame.K_RETURN:
                self.controller.open_interface(game, "explore")
            elif mode == "inventory" and event.key == pygame.K_i:
                self.controller.open_interface(game, "explore")
            elif mode == "keypad":
                if event.key == pygame.K_BACKSPACE:
                    game["code_input"] = game["code_input"][:-1]
                    self.controller.set_feedback(game, "")
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.controller.puzzle.check_cabinet_code(game)
                else:
                    typed_character = event.unicode
                    if typed_character and typed_character in "0123456789":
                        if len(game["code_input"]) < 3:
                            game["code_input"] += typed_character
                            self.controller.set_feedback(game, "")
            elif mode == "symbols" and not game["computer_solved"]:
                if event.key == pygame.K_RETURN:
                    self.controller.puzzle.check_symbol_sequence(game)
                elif event.key == pygame.K_BACKSPACE:
                    game["selected_symbols"] = game["selected_symbols"][:-1]
                    self.controller.set_feedback(game, "")
            elif mode == "power" and event.key == pygame.K_RETURN:
                if not game["power_connected"]:
                    self.controller.puzzle.activate_power(game)
            elif mode == "restart" and event.key == pygame.K_RETURN:
                return "restart"
            elif mode in ("victory", "game_over") and event.key in (pygame.K_r, pygame.K_RETURN):
                return "restart"
        return None

    def handle_click(self, game, position):
        mode = game["mode"]
        if mode not in ("explore", "victory", "game_over") and closebutton.collidepoint(position):
            self.controller.open_interface(game, "explore")
            return None
        if mode == "symbols" and not game["computer_solved"]:
            for index, rect in enumerate(symbolbuttons):
                if rect.collidepoint(position) and len(game["selected_symbols"]) < 3:
                    game["selected_symbols"].append(symbols[index])
                    self.controller.set_feedback(game, "")
            if checkbutton.collidepoint(position):
                self.controller.puzzle.check_symbol_sequence(game)
            elif clearbutton.collidepoint(position):
                game["selected_symbols"] = []
                self.controller.set_feedback(game, "")
        elif mode == "power" and not game["power_connected"]:
            for name, rect in wirerects.items():
                if rect.collidepoint(position):
                    # Each click rotates the tile 90 degrees. The index wraps from 3 to 0.
                    current_rotation = game["wire_rotations"][name]
                    game["wire_rotations"][name] = (current_rotation + 1) % 4
                    self.controller.set_feedback(game, "")
            if activatebutton.collidepoint(position):
                self.controller.puzzle.activate_power(game)
        elif mode in ("restart", "victory", "game_over"):
            if restartbutton.collidepoint(position):
                return "restart"
            if cancelbutton.collidepoint(position):
                if mode in ("victory", "game_over"):
                    return "quit"
                self.controller.open_interface(game, "explore")
        return None


# 8. Draw the current game state
class Renderer:
    def __init__(self, controller):
        self.controller = controller

    def draw_game(self, screen, fonts, game, world):
        self.draw_map(screen, fonts, game, world)
        mode = game["mode"]
        if mode == "explore":
            self.draw_phase_hud(screen, fonts, game)
            return
        titles = {"dialog": game["dialog_title"], "symbols": "Computer Verification",
                  "keypad": "Cabinet Access", "power": "Power Connection",
                  "inventory": "Inventory & Clues", "restart": "Restart game?",
                  "victory": "Laboratory Escape Complete", "game_over": "Game Over"}
        self.draw_window(screen, fonts, titles[mode], closable=mode not in ("victory", "game_over"))
        if mode == "dialog":
            for index, line in enumerate(game["dialog_lines"]):
                self.draw_text(screen, fonts, line, 130, 135 + index * 39)
            if game["dialog_title"].startswith("Workstation "):
                name = game["dialog_title"][-1]
                self.draw_symbol(screen, workstationsymbols[name], (400, 330), 30)
        elif mode == "symbols":
            self.draw_text(screen, fonts, "Enter symbols in this order: C -> A -> B", 130, 120)
            for i, symbol in enumerate(game["selected_symbols"]):
                self.draw_symbol(screen, symbol, (330 + i * 70, 178), 16)
            for symbol, rect in zip(symbols, symbolbuttons):
                pygame.draw.rect(screen, (47, 66, 86), rect, border_radius=7)
                self.draw_symbol(screen, symbol, rect.center)
            self.draw_text(screen, fonts, "Click three symbols. Backspace removes the last one.",
                      160, 299, muted, "small")
            self.draw_button(screen, fonts, checkbutton, "Check / Enter")
            self.draw_button(screen, fonts, clearbutton, "Clear", muted)
        elif mode == "keypad":
            self.draw_text(screen, fonts, "Enter the three-digit code from the computer.", 130, 130)
            displayed_code = game["code_input"].ljust(3, "_")
            self.draw_text(screen, fonts, "  ".join(displayed_code), 400, 225,
                      yellow, "code", True)
            self.draw_text(screen, fonts, "0-9: type    Backspace: delete    Enter: confirm",
                      400, 305, muted, "small", True)
        elif mode == "power":
            self.draw_power_puzzle(screen, fonts, game)
        elif mode == "inventory":
            self.draw_inventory(screen, fonts, game)
        elif mode in ("restart", "victory", "game_over"):
            if mode == "victory":
                self.draw_text(screen, fonts, "Congratulations! You escaped the laboratory.",
                          400, 172, green, center=True)
                self.draw_text(screen, fonts, "Both puzzles solved. All systems restored.",
                          400, 215, muted, center=True)
            elif mode == "game_over":
                self.draw_text(screen, fonts, f"You were hit {maxhits} times. No HP remaining.",
                          400, 165, red, center=True)
                self.draw_text(screen, fonts, "Restart for a fresh attempt with full HP.",
                          400, 207, text, center=True)
                self.draw_text(screen, fonts, "R / Enter: restart    Esc: quit",
                          400, 247, muted, "small", True)
            else:
                self.draw_text(screen, fonts, "Restarting clears all progress in this session.",
                          400, 175, center=True)
                self.draw_text(screen, fonts, "Press Enter to restart, or Esc to cancel.",
                          400, 215, muted, center=True)
            self.draw_button(screen, fonts, restartbutton, "Restart")
            self.draw_button(screen, fonts, cancelbutton,
                        "Quit" if mode in ("victory", "game_over") else "Cancel", muted)
        if game["feedback"]:
            color = green if game["feedback_ok"] else red
            self.draw_text(screen, fonts, game["feedback"], 125, 389, color, "small")
        self.draw_phase_hud(screen, fonts, game)

    def draw_map(self, screen, fonts, game, world):
        screen.fill(background)
        for row in range(12):
            for column in range(20):
                tile = pygame.Rect(column * tilesize, row * tilesize, tilesize, tilesize)
                pygame.draw.rect(screen, (28, 39, 53), tile, 1)
        for wall in world["walls"]:
            pygame.draw.rect(screen, (44, 57, 74), wall)

        can_interact = game["mode"] == "explore" and game["phase"] == "safe"
        nearby = self.controller.player.find_nearby_object(game, world) if can_interact else None
        for obj in world["objects"]:
            color = obj["color"]
            if obj["kind"] == "door" and game["exit_unlocked"]:
                color = (44, 127, 96)
            if obj["kind"] == "cabinet" and game["cabinet_open"]:
                color = (70, 117, 94)
            pygame.draw.rect(screen, color, obj["rect"], border_radius=5)
            if obj is nearby:
                pygame.draw.rect(screen, yellow, obj["rect"].inflate(6, 6), 2, border_radius=5)
            self.draw_text(screen, fonts, obj["label"], *obj["rect"].center,
                      size="small", center=True)
            if obj["kind"] == "station" and obj["name"] in game["symbols_found"]:
                self.draw_symbol(screen, workstationsymbols[obj["name"]],
                            (obj["rect"].centerx, obj["rect"].top - 16), 9, green)

        self.draw_bullets(screen, game)
        player_color = blue
        if game["invincible_time"] > 0:
            player_color = text if int(game["invincible_time"] * 10) % 2 else blue
            pygame.draw.circle(screen, blue, game["player"].center, 21, 2)
        pygame.draw.rect(screen, player_color, game["player"], border_radius=6)
        pygame.draw.circle(screen, text, (game["player"].centerx, game["player"].y + 7), 4)
        message = self.controller.puzzle.current_objective(game)
        if game["phase"] == "barrage":
            message = "WASD: dodge    Tasks locked    Energy bolts pass through furniture."
        if game["notice_time"] > 0:
            message = game["notice"]
        self.draw_text(screen, fonts, message, 22, 453, size="small")
        if nearby is not None:
            prompt = "E: " + nearby["label"]
            px = max(100, min(700, game["player"].centerx))
            py = max(62, game["player"].top - 22)
            label_rect = pygame.Rect(px - 98, py - 13, 196, 26)
            pygame.draw.rect(screen, panel, label_rect, border_radius=5)
            self.draw_text(screen, fonts, prompt, px, py, yellow, "small", True)

    def draw_bullets(self, screen, game):
        for bullet in game["bullets"]:
            x, y = round(bullet["x"]), round(bullet["y"])
            dx, dy = bullet["dx"], bullet["dy"]
            if bullet["warning"] > 0:
                pygame.draw.circle(screen, yellow, (x, y), 10, 2)
                pygame.draw.line(screen, yellow, (x, y), (x + dx * 18, y + dy * 18), 2)
            else:
                pygame.draw.line(screen, red, (x - dx * 15, y - dy * 15), (x, y), 3)
                pygame.draw.circle(screen, red, (x, y), bulletradius)
                pygame.draw.circle(screen, text, (x + dx * 2, y + dy * 2), 2)

    def draw_phase_hud(self, screen, fonts, game):
        danger = game["phase"] == "barrage"
        warning = not danger and game["phase_time"] <= 3
        color = red if danger else (yellow if warning else green)
        label = "DODGE / TASKS LOCKED" if danger else "SAFE / DO TASKS"
        if warning:
            label = "BARRAGE INCOMING"
        if not game["started"]:
            label = "READY / READ INSTRUCTIONS"
        if game["game_won"]:
            label = "ESCAPED / TIMER STOPPED"
            color = green
        elif game["game_over"]:
            label = "GAME OVER / TIMER STOPPED"
            color = red
        pygame.draw.rect(screen, panel, (0, 0, width, 40))
        seconds = f'{game["phase_time"]:.1f}s'
        self.draw_text(screen, fonts, label, 16, 8, color, "small")
        self.draw_text(screen, fonts, seconds, 278, 7, color)
        health = max(0, maxhits - game["hits"])
        health_color = red if health <= 1 else text
        self.draw_text(screen, fonts, f'Wave {game["wave"]}   HP {health}/{maxhits}',
                  365, 8, health_color, "small")
        self.draw_text(screen, fonts, "WASD Move   E Task   I Bag   R Restart", 535, 8, muted, "small")
        duration = barrageduration if danger else safeduration
        bar_width = round(width * max(0, min(1, game["phase_time"] / duration)))
        pygame.draw.rect(screen, color, (0, 34, bar_width, 6))
        if danger:
            pygame.draw.rect(screen, red, (40, 40, 720, 400), 2)
        elif warning and int(game["phase_time"] * 4) % 2:
            pygame.draw.rect(screen, yellow, (40, 40, 720, 400), 2)

    def draw_window(self, screen, fonts, title, closable=True):
        shade = pygame.Surface((width, height), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 175))
        screen.blit(shade, (0, 0))
        pygame.draw.rect(screen, panel, (100, 50, 600, 380), border_radius=12)
        pygame.draw.rect(screen, (65, 88, 110), (100, 50, 600, 380), 2, border_radius=12)
        self.draw_text(screen, fonts, title, 125, 71, size="title")
        if closable:
            self.draw_button(screen, fonts, closebutton, "X", muted)
        self.draw_text(screen, fonts, "Esc: close" if closable else "R: restart    Esc: quit",
                  125, 405, muted, "small")

    def draw_inventory(self, screen, fonts, game):
        self.draw_text(screen, fonts, "RECORDED CLUES", 130, 122, blue)
        for index, name in enumerate(["A", "B", "C"]):
            x = 180 + index * 185
            self.draw_text(screen, fonts, "Station " + name, x, 163, center=True)
            if name in game["symbols_found"]:
                self.draw_symbol(screen, game["symbols_found"][name], (x, 199), 17)
            else:
                self.draw_text(screen, fonts, "?", x, 199, muted, center=True)
        code = cabinetcode if game["computer_solved"] else "not discovered"
        self.draw_text(screen, fonts, "Cabinet code: " + code, 130, 242)
        items = ", ".join(game["inventory"]) if game["inventory"] else "None yet"
        self.draw_text(screen, fonts, "Items: " + items, 130, 277, size="small")
        if game["has_key"]:
            self.draw_text(screen, fonts, "NOTE: Rotate wires to connect generator to exit.",
                      130, 317, yellow, "small")
            self.draw_text(screen, fonts, "Items are used automatically; no need to equip them.",
                      130, 348, muted, "small")

    def draw_power_puzzle(self, screen, fonts, game):
        self.draw_text(screen, fonts, "Click a tile to rotate it 90 degrees clockwise.", 130, 113, size="small")
        wire_color = green if game["power_connected"] else yellow

        for start, end in [((235, 190), (290, 190)), ((480, 190), (535, 190)),
                           ((335, 235), (335, 245)), ((380, 290), (390, 290)),
                           ((435, 235), (435, 245))]:
            pygame.draw.line(screen, wire_color, start, end, 6)
        self.draw_text(screen, fonts, "GENERATOR", 215, 167, green, "small", True)
        self.draw_text(screen, fonts, "EXIT", 555, 167, green, "small", True)
        for name, rect in wirerects.items():
            pygame.draw.rect(screen, (47, 66, 86), rect, border_radius=7)
            pygame.draw.rect(screen, (87, 111, 131), rect, 1, border_radius=7)
            cx, cy = rect.center
            directions = wiredirections[game["wire_rotations"][name]]
            for direction in directions:
                dx, dy = wireoffsets[direction]
                pygame.draw.line(screen, wire_color, (cx, cy), (cx + dx * 45, cy + dy * 45), 7)
            pygame.draw.circle(screen, wire_color, (cx, cy), 6)
            self.draw_text(screen, fonts, name, rect.x + 7, rect.y + 5, text, "small")
        self.draw_button(screen, fonts, activatebutton,
                    "Power Restored" if game["power_connected"] else "Activate Power",
                    green if game["power_connected"] else blue)

    def draw_text(self, screen, fonts, text, x, y, color=text, size="normal", center=False):
        image = fonts[size].render(text, True, color)
        rect = image.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        screen.blit(image, rect)

    def draw_button(self, screen, fonts, rect, label, color=blue):
        pygame.draw.rect(screen, color, rect, border_radius=7)
        self.draw_text(screen, fonts, label, *rect.center, color=background, center=True)

    def draw_symbol(self, screen, symbol, center, radius=18, color=yellow):
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
    Game().main()
