import tdl
__version__ = 1.01
# Set Window.
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 30


def handle_keys():
    """Handles user key input."""
    global playerx, playery
    user_input = tdl.event.key_wait()
    if user_input.key == "ENTER" and user_input.alt:
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


# Init console.
tdl.set_font("dejavu10x10.png", greyscale=True, altLayout=True)
console = tdl.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Umbrella", fullscreen=False)
tdl.setFPS(LIMIT_FPS)

# Set Player ti centre.
playerx = SCREEN_WIDTH//2
playery = SCREEN_HEIGHT//2

# Main loop.
while not tdl.event.is_window_closed():
    console.draw_char(playerx, playery, '@', bg=None, fg=(255,255,255))
    tdl.flush()
    console.draw_char(playerx, playery, ' ', bg=None)
    #handle keys and exit game if needed
    exit_game = handle_keys()
    if exit_game:
        break
