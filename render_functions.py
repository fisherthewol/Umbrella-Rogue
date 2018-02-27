import libtcodpy as libtcod


def render_all(con, entities, game_map, screen_width, screen_height, colours):
    """Draw map and entities."""
    for y in range(game_map.height):
        for x in range(game_map.width):
            wall = game_map.tiles[x][y].block_sight

            if wall:
                libtcod.console_set_char_background(con, x, y, colours.get('dark_wall'), libtcod.BKGND_SET)
            else:
                libtcod.console_set_char_background(con, x, y, colours.get('dark_ground'), libtcod.BKGND_SET)

    for entity in entities:
        draw_entity(con, entity)

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(con, entities):
    """Clear all entities."""
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity):
    """Draw an entity to con."""
    libtcod.console_set_default_foreground(con, entity.color)
    libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)


def clear_entity(con, entity):
    """Clear an entity from con."""
    libtcod.console_put_char(con, entity.x, entity.y, " ", libtcod.BKGND_NONE)
