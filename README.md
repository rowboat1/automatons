# automatons
This is a simple cellular automaton that grows on a map that you either 
provide or randomly generate.


## How does it work?

New cells have a strength value somewhere between 0 and 10.

Each step of the simulation, each cell:
- Creates a child on a random neighbouring ground tile.
- Loses 1 strength
- If the cell reaches 0 strength, it dies
- If the cell has too many neighbours, it dies.

When a child is born onto a neighbouring tile:
- If there is another cell of the same faction, the child is not born, and the 
cell on that tile instead gains strength
- If there is another cell of a different faction, the two fight. The cell with
the higher strength survives

## Key bindings

- SPACE BAR: Pauses the simulation and changes the display mode to show the
territory that each faction currently controls.
- F: Flips the tile under the mouse cursor from ocean to tile or vice versa.
- C: With the game paused, changes the color of the faction under the mouse
cursor.
- Q: Splits the largest faction in two. If the faction's terrain is taller than 
it is wide, the split along a horizontal axis. If it's wider than it is tall, it
will split along a vertical axis.
- R: Randomly places three cells of each faction on the map.

## Maps

There is a map of the United States and a map of Australia provided.

mapping.py will parse a .png file of fully green (#00ff00) and fully
blue (#0000ff) pixels