import tdl
__version__ = 1.00
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 30
tdl.set_font("dejavu10x10.png", greyscale=True, altLayout=True)
console = tdl.init(SCREEN_WIDTH,
                   SCREEN_HEIGHT,
                   title="Umbrella-Rogue",
                   fullscreen = False)
tdl.setFPS(LIMIT_FPS)
while not tdl.event.is_window_closed():
    console.draw_char(1, 1, "@", bg=None, fg=(255,255,255))
    tdl.flush()
