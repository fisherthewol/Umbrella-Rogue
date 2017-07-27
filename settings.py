"""Settings file for Umbrella Rogue.

The main file pulls this through import and sets it at the beginning of the
file.
Having this in a seperate file allows for user/dev customisation. Also allows
for less "boring blocks" of definitions at the start if the value is only used
once.
"""

"""GUI/Window settings."""
screen_width = 80
screen_height = 50
map_width = 80
map_height = 43
fps = 60
bar_width = 20
panel_height = 7
inventory_width = 50

"""Dungeon Generation."""
room_min_size = 6
room_max_size = 10
max_rooms = 30
max_room_monsters = 3
max_room_items = 2

"""FOV settings."""
fov_algo = "BASIC"
fov_light_walls = True
torch_radius = 10

"""Spells quantities."""
heal_amount = 4
lightning_damage = 20
lightning_range = 5
confuse_no_turns = 10
confuse_range = 8
