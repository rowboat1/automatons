import pygame

clock = pygame.time.Clock()
vec = pygame.math.Vector2
pygame.font.init()
font = pygame.font.SysFont("", 20)
pygame.init()

for col in ['RED','BLUE','GREEN','MAGENTA','YELLOW','CYAN','BLACK','WHITE','ORANGE']:
    vars()[col] = pygame.Color(col.lower())

#run this function as game_loop,main_s = pgd_init(size,size)
def pgd_init(width,height,bg_color=(0,0,0),input_dict=None,on_quit=exit):
    main_s = pygame.display.set_mode((width, height))
    def game_loop(display_func):
        def wrapper():
            while 1:
                clock.tick(60)
                main_s.fill(bg_color)
                display_func()
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        on_quit()
                    elif event.type == pygame.KEYDOWN:
                        the_key = pygame.key.name(event.key)
                        if the_key == "escape":
                            on_quit()
                        if input_dict != None:
                            print(the_key)
                            if the_key in input_dict:
                                input_dict[the_key]()
        return wrapper
    return game_loop,main_s
