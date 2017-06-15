import tdl
__version__ = 1.00
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 30
tdl.set_font("dejavu.png", greyscale=True, altLayout=True)
console = tdl.init(SCREEN_WIDTH,
                   SCREEN_HEIGHT,
                   title="Umbrella-Rogue",
                   fullscreen = False)
