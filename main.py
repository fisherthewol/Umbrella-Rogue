import tdl
__version__ = 1.02
# Set Window.
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 30


class GameObject:
    """Generic Object."""
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx, dy):
        """Move by given values"""
        self.x += dx
        self.y += dy

    def draw(self):
        """Draw character representing object."""
        con.draw_char(self.x, self.y, self.char, self.char, self.color)

    def clear(self):
        """Remove  character representing object at previous position."""
        con.draw_char(self)


def handle_keys():
    """Handles user key input."""
    global playerx, playery
    user_input = tdl.event.key_wait()
    if user_input.key == "ENTER" and user_input.control:
        tdl.set_fullscreen(not tdl.get_fullscreen())
    elif user_input.key == "ESCAPE":
        return True  #exit game
    elif user_input.key == "UP":
        playery -= 1
    elif user_input.key == "DOWN":
        playery += 1
    elif user_input.key == "LEFT":
        playerx -= 1
    elif user_input.key == "RIGHT":
        playerx += 1


# Init consoles.
tdl.set_font("dejavu10x10.png", greyscale=True, altLayout=True)
con = tdl.Console(SCREEN_WIDTH, SCREEN_HEIGHT)
root = tdl.init(SCREEN_WIDTH,
                SCREEN_HEIGHT,
                title="Umbrella",
                fullscreen=False)

tdl.setFPS(LIMIT_FPS)

# Set Player to centre.
player = GameObject(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, "@", (255,255,255))
npc = GameObject(SCREEN_WIDTH//2 - 5, SCREEN_HEIGHT//2, "@", (255,255,0))
objects = [npc, player]

# Main loop.
while not tdl.event.is_window_closed():
    con.draw_char(playerx, playery, '@', bg=None, fg=(255,255,255))
    root.blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)
    tdl.flush()
    con.draw_char(playerx, playery, ' ', bg=None)
    #handle keys and exit game if needed
    exit_game = handle_keys()
    if exit_game:
        break
