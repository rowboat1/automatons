from __future__ import annotations
import math
from pygamedefaults import *
import random
import mapping

width,height = 800,800

size = 8

n_tiles_x = width//size
n_tiles_y = height//size

map_file = "usa2.png"

mapping.set_map(size, map_file)

buffer = 1
adj_size = size-buffer

colors = ['red','magenta','white','orange']
tiles = []
tiledict = {x: [] for x in range(n_tiles_x)}
cells = []
cities = []
factions = []
ground_chance = 0.8
city_threshold = 200
city_buff = 3
city_buff_radius = 3
max_neighbors = 4
simulation_paused = False

class Tile:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.has_cell = None
        self.has_city = None
        self.has_city_buff = None
        self.zone_color = None
        self.rect = pygame.Rect(
            self.x * size, 
            self.y * size, 
            adj_size, 
            adj_size
        )
        tiledict[x].append(self)
        tiles.append(self)

    def set_zone_color(self, color: pygame.Color):
        self.zone_color = color

    def get_zone_color(self):
        return self.zone_color

    def get_neighbors(self):
        return self.tiles_in_radius(1)

    def tiles_in_radius(self,radius):
        retval = []
        x_start = max(0, self.x-radius)
        x_end = min(n_tiles_x-1, self.x + radius)
        y_start = max(0, self.y - radius)
        y_end = min(n_tiles_y-1, self.y + radius)
        for x in range(x_start, x_end+1):
            retval += tiledict[x][y_start:y_end+1]
        return retval

    def get_direction(self,other):
        return ((self.x - other.x) < 0, (self.y - other.y) < 0)

    def display(self):
        pygame.draw.rect(main_s, self.color, self.rect)

class Ground(Tile):
    def __init__(self, x, y):
        self.color = 'green'
        Tile.__init__(self, x, y)

    def display(self):
        if simulation_paused:
            if self.zone_color:
                pygame.draw.rect(main_s, self.zone_color, self.rect)
            else:
                pygame.draw.rect(main_s, 'green', self.rect)
        else:
            super().display()

class Ocean(Tile):
    def __init__(self, x, y):
        self.color = 'blue'
        Tile.__init__(self, x, y)

    def stream_check(self):
        if len([n for n in self.get_neighbors() if isinstance(n,Ocean)]) == 1:
            flip(self.x, self.y)

class City:
    def __init__(self, faction: Faction, tile: Tile):
        self.faction = faction
        self.tile = tile
        tile.has_city = self
        for tile in self.tile.tiles_in_radius(city_buff_radius):
            tile.has_city_buff = self.faction
        cities.append(self)

    def join_faction(self, new_faction: Faction):
        self.faction = new_faction

    def swap_faction(self, new_faction: Faction):
        self.tile.has_city.faction = new_faction
        for tile in self.tile.tiles_in_radius(city_buff_radius):
            tile.has_city_buff = new_faction

    def produce(self):
        eligible_tiles = [
            n for n in self.tile.get_neighbors() if isinstance(n, Ground)
        ]
        if eligible_tiles:
            Cell(self.faction,random.choice(eligible_tiles))

    def display(self):
        pygame.draw.circle(main_s, 'black' , self.tile.rect.center, (size+2))
        pygame.draw.circle(
            main_s,
            self.faction.color,
            self.tile.rect.center,
            size
        )

class Faction:
    def __init__(self,color):
        self.color = color
        factions.append(self)

    def get_cities(self):
        return [city for city in cities if city.faction == self]

    def get_city_count(self):
        return len(self.get_cities())

    def get_cells(self):
        return [cell for cell in cells if cell.faction == self]

    def get_centre_of_cells(self):
        all_x = [c.tile.x for c in self.get_cells()]
        all_y = [c.tile.y for c in self.get_cells()]
        c_x = sum(all_x) // len(all_x)
        c_y = sum(all_y) // len(all_y)
        return (c_x, c_y)

    def get_centre_of_cities(self):
        all_x = [c.tile.x for c in self.get_cities()]
        all_y = [c.tile.y for c in self.get_cities()]
        c_x = sum(all_x) // len(all_x)
        c_y = sum(all_y) // len(all_y)
        return (c_x, c_y)

    def split(self, new_faction: Faction):
        centre_of_cells = self.get_centre_of_cells()
        cities = self.get_cities()
        cells = self.get_cells()
        if len(cities) > 0:
            centre_of_cities = self.get_centre_of_cities()
            true_centre = (
                (centre_of_cells[0] + centre_of_cities[0])//2,
                (centre_of_cells[1] + centre_of_cities[1])//2
            )
        else:
            true_centre = centre_of_cells
        for c in cells + cities:
            if c.tile.x <= true_centre[0]:
                c.join_faction(new_faction)

    def best_city_tiles(self):
        c1 = self.get_centre_of_cells()
        centre_of_cells = tiledict[c1[0]][c1[1]]
        if len(self.get_cities()) > 0:
            c2 = self.get_centre_of_cities()
            centre_of_cities = tiledict[c2[0]][c2[1]]
            t1 = centre_of_cells.get_direction(centre_of_cities)
            my_tiles = [
                c.tile for c in self.get_cells() if not c.tile.has_city_buff
            ]
            return [
                t for t in my_tiles if t.get_direction(centre_of_cells) == t1
            ]
        else:
            return [cell.tile for cell in self.get_cells()]

    def make_city(self):
        City(self,random.choice(self.best_city_tiles()))

    def city_check(self):
        if (len(self.get_cells()) // city_threshold) > self.get_city_count():
            self.make_city()

class Cell:
    def __init__(self,faction,tile):
        self.faction = faction
        self.tile = tile
        self.x = tile.x
        self.y = tile.y
        self.strength = random.randrange(10)
        self.tile.has_cell = self
        if self.tile.has_city:
            self.tile.has_city.swap_faction(self.faction)
        cells.append(self)

    def join_faction(self,new_faction):
        self.faction = new_faction

    def die(self):
        cells.remove(self)
        self.tile.has_cell = None

    def get_strength(self):
        retval = self.strength
        if self.tile.has_city_buff == self.faction:
            retval += city_buff
        return retval

    def fight(self, target: Cell) -> bool:
        if self.get_strength() > target.get_strength():
            target.die()
            retval = True
        elif self.strength == target.strength:
            a = random.choice([self,target])
            a.die()
            retval = a == target
        else:
            self.die()
            retval = False
        return retval

    def death_check(self) -> bool:
        retval = False
        crowd = len([n for n in self.tile.get_neighbors() if n.has_cell])
        if crowd > max_neighbors:
            retval = True
        elif self.get_strength() == 0:
            retval = True
        return retval

    def move(self):
        possibles = [n for n in self.tile.get_neighbors()]
        #I'd like to simplify so there's only one self.die() call
        if self.death_check():
            self.die()
        else:
            t = random.choice(possibles)
            if isinstance(t, Ground):
                if not t.has_cell:
                    Cell(self.faction, t)
                else:
                    if self.fight(t.has_cell):
                        Cell(self.faction, t)
            else:
                self.die()
            if self.strength > 0:
                self.strength -= 1


    def display(self):
        pygame.draw.rect(main_s, self.faction.color, self.tile.rect)


if map_file:
    with open("themap.txt") as map_string:
        maplines = map_string.readlines()
        for y in range(len(maplines)):
            for x in range(len(maplines[y]) - 1):
                tile_type = maplines[y][x]
                if tile_type == "g":
                    Ground(x,y)
                else:
                    Ocean(x,y)
else:
    for x in range(n_tiles_x):
       for y in range(n_tiles_y):
           ground_roll = random.uniform(0,1)
           if ground_roll < ground_chance:
               Ground(x,y)
           else:
               Ocean(x,y)


for c in colors:
    Faction(c)

def flip(x,y):
    target = tiledict[x][y]
    if isinstance(target,Ground):
        tiledict[x][y] = Ocean(x,y)
    else:
        tiledict[x][y] = Ground(x,y)
    tiles.remove(target)

def flip_at_mouse():
    x,y = pygame.mouse.get_pos()
    x = x//size
    y = y//size
    flip(x,y)

def get_random_color():
    new_color = (
        random.randrange(255), 
        random.randrange(255), 
        random.randrange(255)
    )
    # Don't want these colours to be too near green or blue
    d1 = math.sqrt(new_color[0]**2 + (255 - new_color[1])**2 + new_color[2]**2)
    d2 = math.sqrt(new_color[0]**2 + new_color[1]**2 + (255 - new_color[2])**2)
    print(d1, d2)
    if d1 < 200 or d2 < 200:
        return get_random_color()
    else:
        return new_color

def split_faction():
    dead_colours = [
        faction for faction in factions if len(faction.get_cells()) == 0
    ]
    biggest = max(factions, key=lambda faction: len(faction.get_cells()))
    if len(dead_colours) > 0:
        revived = dead_colours[0]
        biggest.split(revived)
    else:
        new_color = get_random_color()
        new_faction = Faction(new_color)
        biggest.split(new_faction)

def stream_check_mouse():
    x,y = pygame.mouse.get_pos()
    x = x//size
    y = y//size
    try:
        tiledict[x][y].stream_check()
    except:
        pass

def gen_cell():
    for _ in range(3):
        for faction in factions:
            home_square = random.choice(
                [tile for tile in tiles if isinstance(tile, Ground)]
            )
            Cell(faction,home_square)

def set_all_zone_colors():
    # Initiate a dictionary with each ground tile...
    all_grounds = [tile for tile in tiles if isinstance(tile, Ground)]
    claim_dict = {tile: set() for tile in all_grounds}
    unclaimed_tiles = set(all_grounds)
    
    # Now, we will take the set of all inhabited tiles 
    # and claim them for their respective factions
    seen_this_turn = set()
    for cell in cells:
        seen_this_turn.add(cell.tile)
        claim_dict[cell.tile] = set([cell.faction])
    
    # Now, check all the neighbours of what we saw last turn
    while len(seen_this_turn) > 0:
        unclaimed_tiles -= seen_this_turn
        seen_last_turn = seen_this_turn.copy()
        seen_this_turn = set()
        for tile in seen_last_turn:
            if len(claim_dict[tile]) == 1:
                claimables = set(tile.get_neighbors()) & unclaimed_tiles
                faction = list(claim_dict[tile])[0]
                for tile in claimables:
                    claim_dict[tile].add(faction)
                seen_this_turn |= claimables
    
    for tile, factions in claim_dict.items():
        if len(factions) == 1:
            tile.set_zone_color(list(factions)[0].color)
        elif len(factions) > 1:
            color = random.choice(list(factions)).color
            tile.set_zone_color(color)
        else:
            tile.set_zone_color(None)

def pause():
    global simulation_paused
    simulation_paused = not simulation_paused
    if simulation_paused:
        set_all_zone_colors()

def change_color_at_mouse():
    # Behaviour only guaranteed when paused because the sim moves fast.
    if simulation_paused:
        x, y = pygame.mouse.get_pos()
        x = x//size
        y = y//size
        try:
            color = tiledict[x][y].get_zone_color()
            if color != None:
                # Should only be one, but you never know.
                factions_with_color = [
                    faction for faction in factions if faction.color == color
                ]
                for faction in factions_with_color:
                    faction.color = get_random_color()
            # Now need to repaint zone colors
            set_all_zone_colors()
        except:
            pass

all_inputs = {
    "r":gen_cell,
    "f":flip_at_mouse,
    "s":stream_check_mouse,
    "q":split_faction,
    "c": change_color_at_mouse,
    "space": pause,
}

game_loop,main_s = pgd_init(width,height,input_dict=all_inputs)

for f in factions:
    home_square = random.choice(
        [t for t in tiles if isinstance(t,Ground) and not t.has_city_buff]
    )
    City(f,home_square)

for ocean in [tile for tile in tiles if isinstance(tile,Ocean)]:
    ocean.stream_check()

@game_loop
def step():
    for tile in tiles:
        tile.display()
    for cell in cells:
        cell.display()
        if not simulation_paused:
            cell.move()
    for city in cities:
        if not simulation_paused:
            city.produce()
        city.display()
    if not simulation_paused:
        for faction in factions:
            faction.city_check()

if __name__ == "__main__":
    step()