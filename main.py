#!/usr/bin/env python3
import tdl
from random import randint
import colors
import math
import textwrap
import settings
from tcod import image_load
import shelve
import time

# GUI/Window settings.
SCREEN_WIDTH = settings.screen_width
SCREEN_HEIGHT = settings.screen_height
MAP_WIDTH = settings.map_width
MAP_HEIGHT = settings.map_height
REALTIME = False
LIMIT_FPS = settings.fps
BAR_WIDTH = settings.bar_width
PANEL_HEIGHT = settings.panel_height
INVENTORY_WIDTH = settings.inventory_width
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1


# Tile Colours.
color_dark_wall = (0, 0, 100)
color_light_wall = (130, 110, 50)
color_dark_ground = (50, 50, 150)
color_light_ground = (200, 180, 50)


class Tile:
    """Tile on map."""
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.explored = False
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight


class Rect:
    """A rectangle - Usually a room."""
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        """Return coordinates of center of room."""
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersect(self, other):
        """Returns True if self intersects with other."""
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class GameObject:
    """Generic Object."""
    def __init__(self, x, y, char, name, fg, bg=None, blocks=False,
                 fighter=None, ai=None, item=None):
        self.x = x
        self.y = y
        self.char = char
        self.fg = fg
        self.bg = bg
        self.name = name
        self.blocks = blocks
        # Components.
        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self
        self.ai = ai
        if self.ai:
            self.ai.owner = self
        self.item = item
        if self.item:
            self.item.owner = self

    def move(self, dx, dy):
        """Move by given amount (if not blocked)."""
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def move_towards(self, target_x, target_y):
        """Move towards target."""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def distance_to(self, other):
        """Return distance to other object."""
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def draw(self):
        """Draw obj on screen."""
        global visible_tiles
        if (self.x, self.y) in visible_tiles:
            con.draw_char(self.x, self.y, self.char, self.fg, bg=None)

    def clear(self):
        """Clear obj from screen."""
        con.draw_char(self.x, self.y, " ", self.fg, bg=None)

    def send_to_back(self):
        """Stop this object drawing over others."""
        global objects
        objects.remove(self)
        objects.insert(0, self)


class Fighter:
    """Combat Properties for Objects."""
    def __init__(self, hp, defense, power, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.death_function = death_function

    def take_damage(self, damage):
        """Reduce HP by damage dealt."""
        if damage > 0:
            self.hp -= damage

            if self.hp <= 0:
                func = self.death_function
                if func is not None:
                    func(self.owner)

    def attack(self, target):
        """Deal Damage to target."""
        damage = self.power - target.fighter.defense
        parentname = self.owner.name.capitalize()
        if damage > 0:
            message("{} attacks {} for {} hp.".format(parentname,
                                                      target.name,
                                                      damage),
                    colors.flame)
            target.fighter.take_damage(damage)
        else:
            message("{} attacks {}, but it has no effect!".format(parentname,
                                                                  target.name),
                    colors.flame)

    def heal(self, amount):
        """Heal by given amount, without going over."""
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp


class BasicMonster:
    """Basic Monster AI."""
    def take_turn(self):
        monster = self.owner
        if (monster.x, monster.y) in visible_tiles:
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)


class ConfusedMonster:
    """AI for a confused monster."""
    def __init__(self, old_ai, num_turns=settings.confuse_no_turns):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0:
            self.owner.move(randint(-1, 1), randint(-1, 1))
            self.num_turns -= 1
        else:
            self.owner.ai = self.old_ai
            message("The {} is no longer confused!".format(self.owner.name),
                    colors.amber)


class Item:
    """Item that can be in inv. and used."""
    def __init__(self, use_function=None):
        self.use_function = use_function

    def use(self):
        """Call use function if defined."""
        if self.use_function is None:
            message("The {} cannot be used.".format(self.owner.name),
                    colors.amber)
        else:
            if self.use_function() != "cancelled":
                player.inventory.remove(self.owner)

    def pick_up(self):
        """Add to inventory and remove from map."""
        if len(player.inventory) >= 26:
            message("Inventory full, "
                    "cannot pickup {}.".format(self.owner.name),
                    colors.amber)
        else:
            player.inventory.append(self.owner)
            objects.remove(self.owner)
            message("You picked up a {}!".format(self.owner.name),
                    colors.green)

    def drop(self):
        """Add item to map and remove from inventory."""
        objects.append(self.owner)
        player.inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message("You dropped a {}".format(self.owner.name), colors.amber)


def is_blocked(x, y):
    """Tests if given coords are blocked/blocking."""
    if my_map[x][y].blocked:
        return True
    for obj in objects:
        if obj.blocks and obj.x == x and obj.y == y:
            return True
    return False


def create_room(room):
    """Create room on map from Rect class."""
    global my_map
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            my_map[x][y].blocked = False
            my_map[x][y].block_sight = False


def create_h_tunnel(x1, x2, y):
    """Create horizontal Tunnel."""
    global my_map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        my_map[x][y].blocked = False
        my_map[x][y].block_sight = False


def create_v_tunnel(y1, y2, x):
    """Create Vertical Tunnel."""
    global my_map
    for y in range(min(y1, y2), max(y1, y2) + 1):
        my_map[x][y].blocked = False
        my_map[x][y].block_sight = False


def is_visible_tile(x, y):
    """Test if tile at coords is visible."""
    global my_map
    if x >= MAP_WIDTH or x < 0:
        return False
    elif y >= MAP_HEIGHT or y < 0:
        return False
    elif my_map[x][y].blocked == True:
        return False
    elif my_map[x][y].block_sight == True:
        return False
    else:
        return True


def make_map():
    """Make rooms and tunnels and map, on map."""
    global my_map, objects
    objects = [player]

    # Make map of filled tiles.
    my_map = [[ Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]
    rooms = []
    num_rooms = 0

    for r in range(settings.max_rooms):
        # Random width, height, position inside map.
        w = randint(settings.room_min_size, settings.room_max_size)
        h = randint(settings.room_min_size, settings.room_max_size)
        x = randint(0, MAP_WIDTH-w-1)
        y = randint(0, MAP_HEIGHT-h-1)
        # Create room from rect class.
        new_room = Rect(x, y, w, h)
        # Check if other rooms would intersect this one.
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            # Therefore, room doesn't intersect.
            # Draw room and get center of it.
            create_room(new_room)
            (new_x, new_y) = new_room.center()
            # If first room, center player.
            if num_rooms == 0:
                player.x = new_x
                player.spawnx = new_x
                player.y = new_y
                player.spawny = new_y
            else:
                # Otherwise, connect with tunnels.
                (prev_x, prev_y) = rooms[num_rooms-1].center()
                # 50/50 whether we go vert-hori or hori-vert.
                if randint(0, 1):
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            place_objects(new_room)
            rooms.append(new_room)
            num_rooms += 1


def place_objects(room):
    """Add Monsters/Items to rooms."""
    num_monsters = randint(0, settings.max_room_monsters)
    for i in range(num_monsters):
        x = randint(room.x1+1, room.x2-1)
        y = randint(room.y1+1, room.y2-1)
        if not is_blocked(x, y):
            if randint(0, 100) < 80:
                fighter_component = Fighter(hp=10,
                                            defense=0,
                                            power=3,
                                            death_function=monster_death)
                ai_component = BasicMonster()
                monster = GameObject(x, y, "o", "orc",
                                     colors.desaturated_green,
                                     blocks=True, fighter=fighter_component,
                                     ai=ai_component)
            else:
                fighter_component = Fighter(hp=16,
                                            defense=1,
                                            power=4,
                                            death_function=monster_death)
                ai_component = BasicMonster()
                monster = GameObject(x, y, "T", "troll", colors.darker_green,
                                     blocks=True, fighter=fighter_component,
                                     ai=ai_component)
            objects.append(monster)

    num_items = randint(0, settings.max_room_items)
    for i in range(num_items):
        x = randint(room.x1+1, room.x2-1)
        y = randint(room.y1+1, room.y2-1)

        if not is_blocked(x, y):
            dice = randint(0, 100)
            if dice < 70:
                item_component = Item(use_function=cast_heal)
                item = GameObject(x, y, "!", "healing potion", colors.violet,
                                  item=item_component)
            elif dice < 70+10:
                item_component = Item(use_function=cast_lightning)
                item = GameObject(x, y, "#", "scroll of lightning",
                                  colors.light_yellow, item=item_component)
            elif dice < 70+10+10:
                item_component = Item(use_function=cast_fireball)
                item = GameObject(x, y, "#", "scroll of fireball",
                                  colors.red, item=item_component)
            else:
                item_component = Item(use_function=cast_confuse)
                item = GameObject(x, y, "#", "scroll of confusion",
                                  colors.purple, item=item_component)

            objects.append(item)
            item.send_to_back()


def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    """Draw GUI bar."""
    bar_width = int(float(value) / maximum * total_width)
    panel.draw_rect(x, y, total_width, 1, None, bg=back_color)
    if bar_width > 0:
        panel.draw_rect(x, y, bar_width, 1, None, bg=bar_color)
    text = name + ": " + str(value) + "/" + str(maximum)
    x_centered = x + (total_width-len(text))//2
    panel.draw_str(x_centered, y, text, fg=colors.white, bg=None)


def get_names_under_mouse():
    """Get name of objects under mouse."""
    global visible_tiles
    (x, y) = mouse_coord
    names = [obj.name for obj in objects
        if obj.x == x and obj.y == y and (obj.x, obj.y) in visible_tiles]
    names = ", ".join(names)
    return names.capitalize()


def render_all():
    """Render FOV, tiles and objects."""
    global fov_recompute
    global visible_tiles
    if fov_recompute:
        fov_recompute = False
        visible_tiles = tdl.map.quickFOV(player.x, player.y,
                                         is_visible_tile,
                                         fov=settings.fov_algo,
                                         radius=settings.torch_radius,
                                         lightWalls=settings.fov_light_walls)
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = (x, y) in visible_tiles
                wall = my_map[x][y].block_sight
                if not visible:
                    if my_map[x][y].explored:
                        if wall:
                            con.draw_char(x, y, None, fg=None,
                                          bg=color_dark_wall)
                        else:
                            con.draw_char(x, y, None, fg=None,
                                          bg=color_dark_ground)
                else:
                    if wall:
                        con.draw_char(x, y, None, fg=None, bg=color_light_wall)
                    else:
                        con.draw_char(x, y, None, fg=None,
                                      bg=color_light_ground)
                    my_map[x][y].explored = True
    for obj in objects:
        if obj != player:
            obj.draw()
    player.draw()

    # Blit the contents of "con" to the root console and present it.
    root.blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0)

    # Draw gui panel.
    panel.clear(fg=colors.white, bg=colors.black)
    y = 1
    for (line, color) in game_msgs:
        panel.draw_str(MSG_X, y, line, bg=None, fg=color)
        y += 1

    render_bar(1, 1, BAR_WIDTH, "HP", player.fighter.hp, player.fighter.max_hp,
               colors.light_red, colors.darker_red)

    panel.draw_str(1, 0, get_names_under_mouse(), bg=None,
                   fg=colors.light_gray)

    root.blit(panel, 0, PANEL_Y, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0)


def message(new_msg, color=colors.white):
    """Func for displaying message to GUI."""
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
    for line in new_msg_lines:
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]
        game_msgs.append((line, color))


def player_move_or_attack(dx, dy):
    """Move by dx or dy; if move into monster, attack."""
    global fov_recompute
    x = player.x + dx
    y = player.y + dy
    target = None
    for obj in objects:
        if obj.fighter and obj.x == x and obj.y == y:
            target = obj
            break

    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True


def menu(header, options, width):
    """Create and draw menu screen."""
    if len(options) > 26:
        raise ValueError("Menu cannot have more than 26 options.")

    header_wrapped = textwrap.wrap(header, width)
    header_height = len(header_wrapped)
    height = len(options) + header_height

    window = tdl.Console(width, height)
    window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
    for i, line in enumerate(header_wrapped):
        window.draw_str(0, 0+i, header_wrapped[i])

    y = header_height
    letter_index = ord("a")
    for option_text in options:
        text = "(" + chr(letter_index) + ")" + option_text
        window.draw_str(0, y, text, bg=None)
        y += 1
        letter_index += 1

    x = SCREEN_WIDTH//2 - width//2
    y = SCREEN_HEIGHT//2 - height//2
    root.blit(window, x, y, width, height, 0, 0)

    tdl.flush()
    key = tdl.event.key_wait()
    key_char = key.char
    if key_char == "":
        key_char = " "  # TODO: PLACEHOLDER

    index = ord(key_char) - ord("a")
    if index >= 0 and index < len(options):
        return index
    return None


def inventory_menu(header):
    """Show menu from inventory as options."""
    if len(player.inventory) == 0:
        options = ["Inventory is empty."]
    else:
        options = [item.name for item in player.inventory]

    index = menu(header, options, INVENTORY_WIDTH)

    if index is None or len(player.inventory) == 0:
        return None
    return player.inventory[index].item


def msgbox(text, width=50):
    """Use menu as message box."""
    menu(text, [], width)


def handle_keys():
    """Handle keys from user."""
    global playerx, playery
    global fov_recompute
    global mouse_coord

    keypress = False
    for event in tdl.event.get():
        if event.type == "KEYDOWN":
            user_input = event
            keypress = True
        if event.type == "MOUSEMOTION":
            mouse_coord = event.cell

    if not keypress:
        return "didnt-take-turn"

    if user_input.key == "ENTER" and user_input.control:
        tdl.set_fullscreen(not tdl.get_fullscreen())
    elif user_input.key == "ESCAPE":
        return "exit"

    if game_state == "playing":
        if user_input.key == "UP":
            player_move_or_attack(0, -1)
        elif user_input.key == "DOWN":
            player_move_or_attack(0, 1)
        elif user_input.key == "LEFT":
            player_move_or_attack(-1, 0)
        elif user_input.key == "RIGHT":
            player_move_or_attack(1, 0)
        else:
            if user_input.text == "g":
                for obj in objects:
                    if obj.x == player.x and obj.y == player.y and obj.item:
                        obj.item.pick_up()
                        break

            if user_input.text == "i":
                chosen_item = inventory_menu("Press key next to item to "
                                             "use it; none-item key to cancel"
                                             " menu.\n")
                if chosen_item is not None:
                    chosen_item.use()

            if user_input.text == "d":
                chosen_item = inventory_menu("Press key to drop item.\n")
                if chosen_item is not None:
                    chosen_item.drop()

            return "didnt-take-turn"


def player_death(player):
    """Death animation for player."""
    global game_state
    game_state = "dead"
    message("You died!", colors.darker_red)
    player.char = "%"
    player.fg = colors.dark_red
    player.name = "Remains of Player".format(player.name)


def monster_death(monster):
    """Death animation for monster."""
    message("{} is dead!".format(monster.name.capitalize()), colors.azure)
    monster.char = "%"
    monster.fg = colors.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = "Remains of {}".format(monster.name)
    monster.send_to_back()


def target_tile(max_range=None):
    """Return position of left-clicked tile in FOV."""
    global mouse_coord
    while True:
        tdl.flush()
        clicked = False
        for event in tdl.event.get():
            if event.type == "MOUSEMOTION":
                mouse_coord = event.cell
            if event.type == "MOUSEDOWN" and event.button == "LEFT":
                clicked = True
            elif ((event.type == 'MOUSEDOWN' and event.button == 'RIGHT') or
                  (event.type == 'KEYDOWN' and event.key == 'ESCAPE')):
                    return (None, None)
        render_all()

        x = mouse_coord[0]
        y = mouse_coord[1]
        if (clicked and mouse_coord in visible_tiles and
           (max_range is None or player.distance(x, y) <= max_range)):
            return mouse_coord


def target_monster(max_range=None):
    """Returns clicked monster in FOV."""
    while True:
        (x, y) = target_tile(max_range)
        if x is None:
            return None

        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:
                return obj


def closest_monster(max_range):
    """Find closest monster in range and FOV."""
    closest_enemy = None
    closest_dist = max_range + 1

    for obj in objects:
        if (obj.fighter) and (not obj == player) and ((obj.x, obj.y) in visible_tiles):
            dist = player.distance_to(obj)
            if dist < closest_dist:
                closest_enemy = obj
                closest_dist = dist
    return closest_enemy


def cast_heal():
    """Heal Player."""
    if player.fighter.hp == player.fighter.max_hp:
        message("You are already at full health. Cancelled.", colors.amber)
        return "cancelled"

    message("Your wounds start to feel better!", colors.violet)
    player.fighter.heal(settings.heal_amount)


def cast_lightning():
    message("Left-click a monster to target it, or right-click to cancel.",
            colors.light_cyan)
    monster = target_monster(settings.lightning_range)
    if monster == None:
        message("Cancelled", colors.amber)
        return "cancelled"

    message("A lightning bolt strikes {} with a loud thunder! "
            "Damage: {}HP.".format(monster.name, settings.lightning_damage),
            colors.light_blue)
    monster.fighter.take_damage(settings.lightning_damage)


def cast_confuse():
    """Confuses selected monster."""
    message("Left-click a monster to target it, or right-click to cancel.",
            colors.light_cyan)
    monster = target_monster(settings.confuse_range)
    if monster is None:
        message("Cancelled.", colors.amber)
        return "cancelled"
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster
    message("The eyes of {} look vacant, "
            "as it stumbles around.".format(monster.name), colors.light_blue)


def cast_fireball():
    """Target tile; throw fireball."""
    message("Left-click a tile to target it, or right-click to cancel.",
            colors.light_cyan)
    (x, y) = target_tile()
    if x is None:
        message("Cancelled", colors.amber)
        return "cancelled"
    message("The fireball explodes, burning everything "
            "within {} tiles!".format(settings.fireball_radius), colors.amber)

    for obj in objects:
        if obj.distance(x, y) <= settings.fireball_radius and obj.fighter:
            message("The {} is burned "
                    "for {}HP!".format(obj.name,
                                       settings.fireball_damage))
            obj.fighter.take_damage(settings.fireball_damage)


def cast_teleport(max_range=settings.teleport_range, x=None, y=None):
    """Target tile; teleport to it."""
    global fov_recompute
    if x is None:
        message("Left-click a tile to target it, or right-click to cancel.",
                colors.light_cyan)
        (x, y) = target_tile()
        if x is None:
            message("Cancelled", colors.amber)
            return "cancelled"
        if player.distance(x, y) <= max_range:
            message("With a zip and a zoom, you teleport to the tile.",
                    colors.blue)
            player.x = x
            player.y = y
            fov_recompute = True
            player.draw()
            render_all()
            tdl.flush()
        else:
            message("Tile out of range; cancelled.", colors.blue)
            return "cancelled"
    else:
        player.x = x
        player.y = y
        fov_recompute = True
        player.draw()
        render_all()
        tdl.flush()


def cast_teleporthome():
    """Recall to spawn."""
    message("With a zip and a zoom, you teleport to spawn.", colors.blue)
    cast_teleport(x=player.spawnx, y=player.spawny)


def save_game():
    """Open an new empty shelf to write data."""
    with shelve.open("savegame/savegame", "n") as savefile:
        savefile["my_map"] = my_map
        savefile["objects"] = objects
        savefile["player_index"] = objects.index(player)
        savefile["inventory"] = player.inventory
        savefile["game_msgs"] = game_msgs
        savefile["game_state"] = game_state


def load_game():
    global my_map, objects, player, game_msgs, game_state

    with shelve.open("savegame/savegame", "r") as savefile:
        my_map = savefile["my_map"]
        objects = savefile["objects"]
        player = objects[savefile["player_index"]]
        player.inventory = savefile["inventory"]
        game_msgs = savefile["game_msgs"]
        game_state = savefile["game_state"]


def new_game():
    """Init GameObjects for new game state."""
    global player, game_msgs, game_state
    # Create player.
    fighter_component = Fighter(hp=30, defense=2, power=5,
                                death_function=player_death)
    player = GameObject(0, 0, "@", "player",
                        colors.white, None, blocks=True,
                        fighter=fighter_component)

    # Generate map (not drawn).
    make_map()
    game_state = "playing"

    # Init player inv.
    item_component = Item(use_function=cast_teleporthome)
    beginscroll = GameObject(player.x, player.y, "#", "scroll of recall",
                             colors.cyan, item=item_component)
    player.inventory = []
    player.inventory.append(beginscroll)
    game_msgs = []
    message("Welcome to Umbrella. Arrow keys to move, g to pickup item, "
            "i for inventory, d for drop. glhf!", colors.amber)


def play_game():
    """Play game (main loop)."""
    global mouse_coord, fov_recompute

    player_action = None
    mouse_coord = (0, 0)
    fov_recompute = True
    con.clear()

    while not tdl.event.is_window_closed():
        render_all()
        tdl.flush()
        for obj in objects:
            obj.clear()
        player_action = handle_keys()
        if player_action == "exit":
            save_game()
            break
        if game_state == "playing" and player_action != "didnt-take-turn":
            for obj in objects:
                if obj.ai:
                    obj.ai.take_turn()


def main_menu():
    img = image_load("menu.png")
    while not tdl.event.is_window_closed():
        img.blit_2x(root, 0, 0)
        choice = menu("", ["Play New", "Continue", "Quit"], 24)
        if choice == 0:
            new_game()
            play_game()
        elif choice == 1:
            try:
                load_game()
            except:
                msgbox("\nNo save game/file corruption.\n", 24)
                time.sleep(4)
                continue
            play_game()
        elif choice == 2:
            break


tdl.set_font("dejavu10x10.png", greyscale=True, altLayout=True)
root = tdl.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Umbrella",
                fullscreen=False)
tdl.setFPS(LIMIT_FPS)
con = tdl.Console(MAP_WIDTH, MAP_HEIGHT)
panel = tdl.Console(SCREEN_WIDTH, PANEL_HEIGHT)

# Start game menu.
main_menu()
