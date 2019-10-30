from pygamedefaults import *
import random

width,height = 800,800

size = 12

n_tiles_x = width//size
n_tiles_y = height//size
buffer = 1

colors = [RED,MAGENTA,BLACK,ORANGE]
tiles = []
tiledict = {x: [] for x in range(n_tiles_x)}
cells = []
cities = []
factions = []
oceans = []
ground_chance = 0.8
city_threshold = 100
city_buff = 3

class Tile(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.has_cell = None
        self.has_city = None
        self.has_city_buff = None
        self.rect = pygame.Rect(self.x*size,self.y*size,(size-buffer),(size-buffer))
        tiledict[x].append(self)
        tiles.append(self)

    def get_neighbors(self):
        retval = []
        x_start = 0 if (self.x == 0) else (self.x - 1)
        x_end = self.x if (self.x == n_tiles_x-1) else self.x + 1
        y_start = 0 if (self.y == 0) else (self.y - 1)
        y_end = self.y if (self.y == n_tiles_y-1) else self.y + 1
        for x in range(x_start, x_end+1):
            retval += tiledict[x][y_start:y_end+1]
        return retval

    def tiles_in_radius(self,radius):
        retval = [self]
        for r in range(radius):
            a = [t for t in retval]
            for tile in a:
                retval += tile.get_neighbors()
        return retval

    def display(self):
        pygame.draw.rect(main_s,self.color,self.rect)

class Ground(Tile):
    def __init__(self,x,y):
        self.color = GREEN
        self.is_ground = True
        Tile.__init__(self,x,y)

class Ocean(Tile):
    def __init__(self,x,y):
        self.color = BLUE
        self.is_ground = False
        oceans.append(self)
        Tile.__init__(self,x,y)

    def stream_check(self):
        if [n.is_ground for n in self.get_neighbors()].count(False) == 1:
            flip(self.x,self.y)

class City(object):
    def __init__(self,faction,tile):
        self.faction = faction
        self.is_ground = True
        self.tile = tile
        tile.has_city = self
        self.faction.cities.append(self)
        self.faction.city_counter += 1
        for tile in self.tile.tiles_in_radius(2):
            tile.has_city_buff = self.faction
        cities.append(self)

    def swap_faction(self,new_faction):
        self.tile.has_city.faction = new_faction
        for tile in self.tile.tiles_in_radius(2):
            tile.has_city_buff = new_faction

    def display(self):
        pygame.draw.circle(main_s,self.faction.color,self.tile.rect.center,size)

class Faction(object):
    def __init__(self,color):
        self.color = color
        self.cells = []
        self.city_counter = 0
        self.cities = []
        factions.append(self)

    def make_city(self):
        City(self,random.choice(self.cells).tile)

    def city_check(self):
        if (len(self.cells) // city_threshold) > self.city_counter:
            self.make_city()

class Cell(object):
    def __init__(self,faction,tile):
        self.faction = faction
        self.color = faction.color
        self.tile = tile
        self.x = tile.x
        self.y = tile.y
        self.strength = random.randrange(10)
        self.tile.has_cell = self
        if self.tile.has_city:
            self.tile.has_city.swap_faction(self.faction)
        self.faction.cells.append(self)
        cells.append(self)

    def die(self):
        cells.remove(self)
        self.faction.cells.remove(self)
        self.tile.has_cell = None

    def get_strength(self):
        retval = self.strength
        if self.tile.has_city_buff == self.faction:
            retval += city_buff
        return retval

    def fight(self,target):
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

    def move(self):
        possibles = [n for n in self.tile.get_neighbors()]
        t = random.choice(possibles)
        if t.is_ground:
            if not t.has_cell:
                Cell(self.faction,t)
            else:
                if self.fight(t.has_cell):
                    Cell(self.faction,t)
        else:
            self.die()
        if self.strength > 0:
            self.strength -= 1


    def display(self):
        pygame.draw.rect(main_s,self.color,self.tile.rect)

#for x in range(n_tiles_x):
#    for y in range(n_tiles_y):
#        ground_roll = random.uniform(0,1)
#        if ground_roll < ground_chance:
#            Ground(x,y)
#        else:
#            Ocean(x,y)

with open("themap.txt") as mapfile:
    maplines = mapfile.readlines()
    for x in range(len(maplines)):
        for y in range(len(maplines[x]) - 1):
            tile_type = maplines[x][y]
            if tile_type == "g":
                Ground(y,x)
            else:
                Ocean(y,x)

for c in colors:
    Faction(c)

def flip(x,y):
    target = tiledict[x][y]
    if target.is_ground:
        tiledict[x][y] = Ocean(x,y)
    else:
        tiledict[x][y] = Ground(x,y)
    tiles.remove(target)

def flip_at_mouse():
    x,y = pygame.mouse.get_pos()
    x = x//size
    y = y//size
    flip(x,y)

def stream_check_mouse():
    x,y = pygame.mouse.get_pos()
    x = x//size
    y = y//size
    tiledict[x][y].stream_check()

def gen_cell():
    for i in range(5):
        for f in factions:
            Cell(f,tiledict[random.randrange(n_tiles_x)][random.randrange(n_tiles_y)])

game_loop,main_s = pgd_init(width,height,input_dict={"r":gen_cell,"f":flip_at_mouse,"s":stream_check_mouse})

gen_cell()

for ocean in oceans:
    ocean.stream_check()

#for t in tiledict[n_tiles_x//2][n_tiles_y//2].tiles_in_radius(2):
#    t.color = WHITE

@game_loop
def step():
    for tile in tiles:
        tile.display()
    for cell in cells:
        cell.display()
        cell.move()
    for city in cities:
        city.display()
    for faction in factions:
        faction.city_check()

step()
