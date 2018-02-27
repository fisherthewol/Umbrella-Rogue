class Entity:
    """Generic Object to represent enities."""
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx, dy):
        """Move self by dx, dy."""
        self.x += dx
        self.y += dy
