# import pygame
import pygame
import sys
import random

# -- import module stuff
import kot2.util
import kot2.ui

# -- configuration
FANCY_DEBUG         = True                      # case you debug fonts to be antialised.
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
        self.worlds             = {}
        self.on_world           = ''
        self.world              = None
        self.world_bg           = None
        self.world_element_cache= {}
        # variables for statistics
        self.world_ticks_counter    = 0
        self.world_draw_counter     = 0
        # calculate the tick time.
        self.tick_time = 0
        self.draw_time = 0
        # init the debug info surface
        self.show_debug_info    = False
        self.debug_surf         = pygame.Surface((128*2,128))
        # real deep down debug
        self.debug = kot2.util.debug.debug_instance()
        self.debug.output_to = sys.stdout if DEBUG_THIS_FILE else None
        self.debug.output_en = DEBUG_THIS_FILE
        self.debug.name_module = "world"

    #
    # CLASS INIT FUNCTIONS
    #
    
    def load_resources(self):
        # load the debug text font, this is the font used on the
        # debug conner you can open by clicking F3.
        self.debug_info_font = self.content.get_font("normal",14)
    
    def load_gui_system(self):
        # -- init the coregui stuff here --
        self.coregui    = kot2.ui.elements.display(self.game_core.window.surface)

    def init(self):
        """ initialize the worlds and the principal engine """
        # Load all the resources that the WORLD needs here. 
        self.load_resources()
        # NOTE: here is loaded the main GUI system for the menu
        # the MENU gui is spliten in this hierachy:
        # (coregui) ->  (main_menu)  -> (audio_options)
        #           |                -> (save options)
        #           |                -> (other options ...)
        #           \   (text box)
        #           |   (warning box)
        self.load_gui_system()
        # TODO: this will load the initial map for now, when the
        # save system be finished, this will no longer be used.
        self.__load_initial_map()

    #
    # INITIAL MAP INTERACTION & SAVE LOAD
    #

    def __load_initial_map(self):
        """ this function will only activate when the map is not loaded yet """
        self.debug.write("initializing the game for the first time!")
        initial_information = self.game_core.initial_config_dict['initial_settings']
        self.load_map(initial_information.get("load_map"))
        self.load_map("boo_city")

    #
    # MAP LOADING & MAP GENERATION FUNCTIONS
    #

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
            
    def __load_elements(self, world_storage, data):
        """
        Load all the world elements.
        ----------------------------
        NOTE: you must have the world already loaded,
        this requires self.world to be a valid pointer
        to the world.
        """
        self.debug.write("loading elements for map: %s" % world_storage.name)
        if not data.get("elements"):
            self.debug.write("map %s don't have a element list." % world_storage.name)
            return
        # NOTE: the world elements textures are stored in the special cache in
        # this class (self.world_element_cache)*, if a world is not used for a
        # long time, it will be recycled to free more memory.
        self.debug.write("there are: %d elements to be loaded." % len(data['elements']))
        for element in data['elements']:
            element_name    = element.get("name")
            element_position= element.get("position")
            element_texture = element.get("texture")
            element_size    = element_texture.get("res")
            element_rect    = pygame.Rect()
            # NOTE: this is a quick information of how elements are organized.

            world_storage.elements.append([
            ])

    def load_map(self, map_name):
        """ the map load data is something like this:
            {"name":X,...} properties. """
        # first, load the map file and then extract the data
        # from there.
        # TODO: assert if the map file exists.
        target_map_dir  = self.content.game_path + "data/" + map_name + ".json"
        self.debug.write("Loading map -- %s"% map_name)
        self.debug.write("Possible Map File: %s" % target_map_dir)
        target_data     = kot2.util.cjson.jsonc_get(target_map_dir)
        # Here is where all the information is put on the proto_world class
        # everything from the size to the floor_texture
        proto_world = m_world_storage()
        proto_world.name        = target_data['properties']['name']
        proto_world.size        = target_data['properties']['map_size']
        proto_world.tex_data    = target_data['properties']['floor_tile_texture']
        proto_world.res_size    = target_data['properties']['floor_tile_texture_res']
        # NOTE: the floor texture is not stored on the map but it's stored
        # on the main class (aka: self), this is done to save memory, many
        # maps loaded with a distinct background would be bad to store, so
        # only one map is loaded per world, meaning they need to reload all
        # the time when it is set.
        self.__generate_background(proto_world)
        self.__load_elements(proto_world, target_data)
        # append on the world storage
        self.worlds[map_name] = proto_world
        self.world = self.worlds[map_name]
        self.on_world = map_name
    
    #
    # MAP CHANGING
    #

    def set_map(self, name):
        """ set the map and not load it again from the file. """
        # assign the new world reference to the world
        # stuff.
        self.world = self.worlds[name]
        self.on_world = name
        # NOTE: update and generate a new background here.
        self.__generate_background(self.world)
    
    def alternate_map(self):
        """ this function will just randomly load a map
            so, it should be removed on the last version.
        """
        # HACK: choice function don't support keys as lists.
        list_words = random.choice(list(self.worlds.keys()))
        self.debug.write("loading random selected world: %s\n" % list_words)
        self.set_map(list_words)
        
    #
    # TICK FUNCTIONS
    #

    def try_move(self, x_dir, y_dir):
        """ try to move the player to some direction """
        self.world.camera_pos[0] += x_dir
        self.world.camera_pos[1] += y_dir

    def __process_keys(self):
        """ process all the keys entries that are continous. """
        keys_pressed    = pygame.key.get_pressed()
        if      keys_pressed[pygame.K_UP]   or keys_pressed[pygame.K_w]:
            self.try_move(0,  self.world.player_speed)
        elif    keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            self.try_move(0, -self.world.player_speed)
        elif    keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            self.try_move( self.world.player_speed, 0)
        elif    keys_pressed[pygame.K_RIGHT]or keys_pressed[pygame.K_d]:
            self.try_move(-self.world.player_speed, 0)

    def __subroutine_functions(self):
        """ subroutine function. """
        self.content.recycle_content()
    
    def __update_guis(self, ev_list):
        """ update the gui system here """
        self.coregui.tick(ev_list)

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
        # update the coregui system.
        # NOTE: this needs to be here because there is some
        # buttons that are triggered by buttons, such as ESC that
        # opens the menu.
        self.__update_guis(ev_list)
        # check the other clicks (for the player) here
        self.__process_keys()
        # NOTE: some sub-routine function
        self.__subroutine_functions()
        # TODO: check only for the ticks on the world
        self.tick_time = pygame.time.get_ticks() - time_0

    #
    # DRAW FUNCTIONS
    #

    def draw_debug_info(self):
        """ the debug info is drawn after the viewport so the debug info
            is basically on the top of everything """
        self.debug_surf.fill((0xFF,0xFF,0xFF))
        texts = [
            "Kot2 '%s'"                     % VERSION,
            "On Map: %s"                    % self.on_world,
            "Position: [%d, %d]"            % (self.world.camera_pos[0],self.world.camera_pos[1]),
            "Resolution: %d"                % self.world.res_size
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
    
    def draw_gui(self):
        """ update the main gui functions """
        self.coregui.draw()

    def draw(self):
        """ draw the game frame """
        self.game_core.window.surface.fill((0, 0, 0))
        # draw the world
        self.world_draw()
        # draw the debug text if possible
        if self.show_debug_info:
            self.draw_debug_info()
        self.draw_gui()
        pygame.display.flip()