import tdl
__version__ = 1.03
# Set Window.
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 45
LIMIT_FPS = 30
color_dark_wall = (0, 0, 100)
color_dark_ground = (8, 8, 68)


class Tile:
    """Map tile object."""
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight


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


def handle_keys():
    """Handles user key input."""
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


def make_map():
    global my_map
    my_map = [[Tile(False)
        for y in range(MAP_HEIGHT)]
            for x in range(MAP_WIDTH)]


# Init consoles.
tdl.set_font("dejavu10x10.png", greyscale=True, altLayout=True)
con = tdl.Console(SCREEN_WIDTH, SCREEN_HEIGHT)
root = tdl.init(SCREEN_WIDTH,
                SCREEN_HEIGHT,
                title="Umbrella",
                fullscreen=False)

tdl.setFPS(LIMIT_FPS)

# Set Player to centre.
player = GameObject(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, "@", (255,255,255), None)
npc = GameObject(SCREEN_WIDTH//2 - 5, SCREEN_HEIGHT//2, "@", (255,255,0), None)
objects = [npc, player]
tmap = make_map()
my_map[30][22].blocked = True
my_map[30][22].block_sight = True
my_map[50][22].blocked = True
my_map[50][22].block_sight = True

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
