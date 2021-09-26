# import pygame
import pygame
# -- configuration
FANCY_DEBUG         = False                     # case you debug fonts to be antialised.
VERSION             = '1.0'                     # set the version here

# -- m_world class begins
class m_world:
    def __init__(self, content, game_core):
        self.content = content
        self.game_core = game_core
        # begin initializing some variables
        # that will be used frequently on the execution
        self.viewport = None
        self.coregui = None
        # when a world is loaded, it is put in the list
        # and it not removed until the max world on the
        # list is not reach.
        # TODO: GC collection on the worlds.
        self.worlds = {}
        self.on_world = ''
        self.world = None
        # variables for statistics
        self.world_ticks = 0
        self.world_draw = 0
        # calculate the tick time.
        self.tick_time = 0
        self.draw_time = 0
        # init the debug info surface
        self.show_debug_info = True
        self.debug_surf = pygame.Surface((128*2,128))
    def init(self):
        """ initialize the worlds and the principal engine """
        # init the debug info variables
        self.debug_info_font = self.content.get_font("normal",14)
    # -- tick functions
    def tick(self, ev_list):
        """ do all the game processing here """
        time_0 = pygame.time.get_ticks()
        for ev in ev_list:
            if ev.type == pygame.QUIT:
                self.game_core.running = False
                return
        # TODO: check only for the ticks on the world
        self.tick_time = pygame.time.get_ticks() - time_0
    # -- draw functions
    def draw_debug_info(self):
        """ the debug info is drawn after the viewport so the debug info
            is basically on the top of everything """
        self.debug_surf.fill((0xFF,0xFF,0xFF))
        texts = [
            "Kot2 '%s'" % VERSION,
            "Tick: %d" % self.tick_time,
            "Draw: %d" % self.draw_time
        ]
        h_space = 0
        for text in texts:
            rendered = self.debug_info_font.render(text,FANCY_DEBUG,(0, 0, 0))
            self.debug_surf.blit(rendered,(0,h_space))
            h_space += rendered.get_height()
        self.game_core.window.surface.blit(self.debug_surf,(0,0))
    def draw(self):
        """ draw the game frame """
        self.game_core.window.surface.fill((0, 0, 0))
        # draw the debug text if possible
        if self.show_debug_info:
            self.draw_debug_info()
        pygame.display.flip()