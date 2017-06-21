import tdl
from random import randint
__version__ = 1.04
# Set Window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 30
# Set Map
MAP_WIDTH = 80
MAP_HEIGHT = 45
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
# Set tiles colours.
color_dark_wall = (0, 0, 100)
color_dark_ground = (5, 66, 22)

class Tile:
    """Map tile object."""
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight


class Rect:
    """Rectangle on map. Usually a Room."""
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class GameObject:
    """Generic Object."""
    def __init__(self, x, y, char, fg, bg):
        self.x = x
        self.y = y
        self.char = char
        self.bg = bg
        self.fg = fg

    def move(self, dx, dy):
        """Move by given values"""
        if not my_map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy

    def draw(self):
        """Draw character representing object."""
        con.draw_char(self.x, self.y, self.char, self.fg, self.bg)

    def clear(self):
        """Remove  character representing object at previous position."""
        con.draw_char(self.x, self.y, " ", self.fg, self.bg)


def create_room(room):
    global my_map
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            my_map[x][y].blocked = False
            my_map[x][y].block_sight = False


def create_h_tunnel(x1, x2, y):
    global my_map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        my_map[x][y].blocked = False
        my_map[x][y].block_sight = False


def create_v_tunnel(y1, y2, x):
    global my_map
    for x in range(min(y1, y2), max(y1, y2) + 1):
        my_map[x][y].blocked = False
        my_map[x][y].block_sight = False


def make_map():
    global my_map

    my_map = [[Tile(True)
        for y in range(MAP_HEIGHT)]
            for x in range(MAP_WIDTH)]

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        w = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = randint(0, MAP_WIDTH-w-1)
        y = randint(0, MAP_HEIGHT-h-1)

        new_room = Rect(x, y, w, h)

        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            create_room(new_room)
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                player.x = new_x
                player.y = new_y

            else:
                (prev_x, prev_y) = rooms[num_rooms-1].center()

                if randint(0, 1):
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_x, new_x, new_y)
                else:
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            rooms.append(new_room)
            num_rooms += 1


def render_all():

    for obj in objects:
        obj.draw()

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = my_map[x][y].block_sight
            if wall:
                con.draw_char(x, y, None, fg=None, bg=color_dark_wall)
            else:
                con.draw_char(x, y, None, fg=None, bg=color_dark_ground)
    root.blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)


def handle_keys():
    """Handles user key input. Currently set for turn-based."""
    global playerx, playery
    user_input = tdl.event.key_wait()
    if user_input.key == "ENTER" and user_input.control:
        tdl.set_fullscreen(not tdl.get_fullscreen())
    elif user_input.key == "ESCAPE":
        return True  #exit game
    elif user_input.key == "UP":
        player.move(0, -1)
    elif user_input.key == "DOWN":
        player.move(0, 1)
    elif user_input.key == "LEFT":
        player.move(-1, 0)
    elif user_input.key == "RIGHT":
        player.move(1, 0)


# Init consoles.
tdl.set_font("dejavu10x10.png", greyscale=True, altLayout=True)
root = tdl.init(SCREEN_WIDTH,
                SCREEN_HEIGHT,
                title="Umbrella",
                fullscreen=False)
con = tdl.Console(SCREEN_WIDTH, SCREEN_HEIGHT)
tdl.setFPS(LIMIT_FPS)

player = GameObject(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, "@", (255,255,255), None)
npc = GameObject(SCREEN_WIDTH//2 - 5, SCREEN_HEIGHT//2, "@", (255,255,0), None)

# Game Objects.
objects = [npc, player]

# Generate map.
tmap = make_map()


# Main loop.
while not tdl.event.is_window_closed():
    render_all()
    tdl.flush()
    for obj in objects:
        obj.clear()
    # Handle keys and exit game if needed.
    exit_game = handle_keys()
    if exit_game:
        break
