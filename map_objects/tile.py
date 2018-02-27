class Tile:
    """Tile on map."""
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        if block_sight is None:
            # If tile blocks passage, it defaults to blocking sight as well.
            block_sight = blocked

        self.block_sight = block_sight
