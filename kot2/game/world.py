# import pygame
import pygame
import sys
import random

# -- import module stuff
import kot2.util

# -- configuration
FANCY_DEBUG         = False                     # case you debug fonts to be antialised.
VERSION             = '1.0'                     # set the version here
DEBUG_THIS_FILE     = True                      # to debug the most internal functions, see here.

# -- m_world_storage: store all the map properties
# such as player local properties, camera position
# and more stuff.
class m_world_storage:
    def __init__(self):
        # store the map name
        self.name = None
        self.generic_name = None
        # map size and it textures
        self.size = [0, 0]
        self.res_size = 0
        self.tex_data = None
        # the entities
        self.entities = []
        self.elements = []
        # player stuff.
        self.camera_pos     = [0, 0]
        self.player_speed   = 4

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
        self.world_bg = None
        # variables for statistics
        self.world_ticks_counter = 0
        self.world_draw_counter = 0
        # calculate the tick time.
        self.tick_time = 0
        self.draw_time = 0
        # init the debug info surface
        self.show_debug_info = False
        self.debug_surf = pygame.Surface((128*2,128))
        # real deep down debug
        self.debug = kot2.util.debug.debug_instance()
        self.debug.output_to = sys.stdout if DEBUG_THIS_FILE else None
        self.debug.output_en = DEBUG_THIS_FILE
        self.debug.name_module = "world"

    def init(self):
        """ initialize the worlds and the principal engine """
        # init the debug info variables
        self.debug_info_font = self.content.get_font("normal",14)
        # init the maps
        # TODO: load the map from the player saving.
        self.__load_initial_map()

    def __load_initial_map(self):
        """ this function will only activate when the map is not loaded yet """
        self.debug.write("initializing the game for the first time!")
        initial_information = self.game_core.initial_config_dict['initial_settings']
        self.load_map(initial_information.get("load_map"))
        self.load_map("boo_city")

    def __generate_background(self, world_storage):
        """ this function will generate a background for a certain level, for
            save memory, the space is one per map."""
        # NOTE: this should debug the end also.
        self.debug.write("generating the background map.")
        size        = world_storage.size
        res_size    = world_storage.res_size
        surfaces    = self.content.get_content_by_spec(world_storage.tex_data)
        self.world_bg = pygame.Surface((
            size[0] * res_size,
            size[1] * res_size
        ))
        for y_index in range(0, size[1]):
            for x_index in range(0,size[0]):
                surface_selected = random.choice(surfaces)
                self.world_bg.blit(
                    surface_selected,
                    (
                        x_index * res_size,
                        y_index * res_size
                    )
                )

    def load_map(self, map_name):
        """ the map load data is something like this:
            {"name":X,...} properties. """
        self.debug.write("opening map = %s!" % map_name)
        target_map_dir  = self.content.game_path + "data/" + map_name + ".json"
        target_data     = kot2.util.cjson.jsonc_get(target_map_dir)
        # begin to extract the map information here
        # and build it using the class.
        proto_world = m_world_storage()
        proto_world.name        = target_data['properties']['name']
        proto_world.size        = target_data['properties']['map_size']
        proto_world.tex_data    = target_data['properties']['floor_tile_texture']
        proto_world.res_size    = target_data['properties']['floor_tile_texture_res']
        # begin to generate a world
        self.__generate_background(proto_world)
        # append on the world storage
        self.worlds[map_name] = proto_world
        self.world = self.worlds[map_name]
        self.on_world = map_name
    
    def set_map(self, name):
        """ set the map and not load it again from the file. """
        self.world = self.worlds[name]
        self.on_world = name
    
    def alternate_map(self):
        # HACK: choice function don't support dumb
        # tuples.
        list_words = random.choice(list(self.worlds.keys()))
        self.debug.write("loading random selected world: %s\n" % list_words)
        self.set_map(list_words)
        
    # -- tick functions
    def try_move(self, x_dir, y_dir):
        """ try to move the player to some direction """
        self.world.camera_pos[0] += x_dir
        self.world.camera_pos[1] += y_dir

    def tick(self, ev_list):
        """ do all the game processing here """
        time_0 = pygame.time.get_ticks()
        for ev in ev_list:
            if ev.type == pygame.QUIT:
                self.game_core.running = False
                return
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_F3:
                    self.show_debug_info = not self.show_debug_info
                if ev.key == pygame.K_F4:
                    self.alternate_map()
        # check the other clicks (for the player) here
        keys_pressed    = pygame.key.get_pressed()
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            self.try_move(0, self.world.player_speed)
        # TODO: check only for the ticks on the world
        self.tick_time = pygame.time.get_ticks() - time_0

    # -- draw functions
    def draw_debug_info(self):
        """ the debug info is drawn after the viewport so the debug info
            is basically on the top of everything """
        self.debug_surf.fill((0xFF,0xFF,0xFF))
        texts = [
            "Kot2 '%s'" % VERSION,
            "On Map: %s" % self.on_world,
            "Tick: %d" % self.tick_time,
            "Draw: %d" % self.draw_time
        ]
        h_space = 0
        for text in texts:
            rendered = self.debug_info_font.render(text,FANCY_DEBUG,(0, 0, 0))
            self.debug_surf.blit(rendered,(0,h_space))
            h_space += rendered.get_height()
        # setup the window now.
        self.game_core.window.surface.blit(self.debug_surf,(0,0))
    
    def world_draw(self):
        self.game_core.window.surface.blit(self.world_bg,self.world.camera_pos)

    def draw(self):
        """ draw the game frame """
        self.game_core.window.surface.fill((0, 0, 0))
        # draw the world
        self.world_draw()
        # draw the debug text if possible
        if self.show_debug_info:
            self.draw_debug_info()
        pygame.display.flip()