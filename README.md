# Umbrella-Rogue
An attempt at a roguelike in python3.  

## Controls:  
- Arrow Keys to move.  
- i Opens use-inventory.  
- d Opens drop-inventory (currently pressing d inside use-inventory uses then opens drop-inventory, be careful).  
- g Grabs item you are stood on.  

## Known Bugs:  
- Monsters attack around corners. This is a priority to fix.  
- When casting recall, the player isn't drawn until a movement is given. I've already tried fixing this in a number of ways, I believe it has something to do with the way tdl works.  

## Projects:  
- Fix above bugs.  
- Implement new levels, both of map and of players/characters (Easily Done).  
- Create new monsters for the levels.  
- Abstract functions into files. This may be hard; at the moment it would result in circular imports, which would be shitty.  
