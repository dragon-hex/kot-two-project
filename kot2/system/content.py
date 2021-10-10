# as like all the modules, import pygame
import pygame
# import some other modules
import kot2.util
from time import gmtime, strftime
import os, sys

# -- begin content storage & provider class:
# provides a image or some asset for the game
# and keeps it in memory.

CONTENT_TYPE_IMAGE      = 1
CONTENT_TYPE_FONT       = 2
CONTENT_TYPE_SPRITE     = 3
CONTENT_TYPE_NAME_IMAGE = 'image'
CONTENT_TYPE_NAME_SPRITE= 'sprite'
CONTENT_TYPE_NAME_FONT  = 'font'

# list of possible errors
RESOURCE_NOT_FOUND      = -1
ERROR_OPENING_RESOURCE  = -2

# some constants (that can be changed on the init)
AVG_TIME_IN_CACHE       = 30 * 1000
DEBUG_THIS_FILE         = True

class content:
    def __init__(self):
        # keep on the cache some stuff
        # for a determined amount of time.
        # init the game path.
        self.game_path          = None
        self.cache              = {
            # CACHE STORE: <NAME_CACHE_REF>: [<CACHE_DATA>, <LIFESPAN_TIME>]
            # NOTE: -1 is permanent on the cache.
            'null': [0, -1]
        }
        # init the debug system
        self.debug = kot2.util.debug.debug_instance()
        self.debug.name_module = "content-provider"
        self.debug.output_to = sys.stdout if DEBUG_THIS_FILE else None
        self.debug.output_en = DEBUG_THIS_FILE
    
    def __handle_exception(self, at, exception):
        """ if you hooked a function to the listener... """
        # TODO: finish this.
        pass
    
    def __sandbox_action(self, function, function_name):
        """ function to make the functions smaller, dummi. """
        self.debug.write("sandbox'ed action = %s" % function_name)
        if DEBUG_THIS_FILE:
            return function()
        else:
            try:
                return function()
            except Exception as E:
                self.__handle_exception(function_name,E)

    def __get_image_raw(self, name, use_prefix=None):
        """ try to import the image and all the stuff """
        possible_dir    = self.game_path + (use_prefix or "images/") + name + ".png"
        self.debug.write("providing content for image: %s" % possible_dir)
        if not os.path.exists(possible_dir):
            return RESOURCE_NOT_FOUND, None
        # -- begin here to get the image.
        def __get_image(): return pygame.image.load(possible_dir)
        image = self.__sandbox_action(__get_image, "__get_image_raw(%s)" % possible_dir)
        return 0, image
    
    def __get_font_raw(self, name, font_size):
        """ try to import a new font """
        possible_dir    = self.game_path + "fonts/" + name + ".ttf"
        self.debug.write("providing content for font: %s" % possible_dir)
        if not os.path.exists(possible_dir):
            return RESOURCE_NOT_FOUND, None
        # -- get the font here
        def __get_font(): return pygame.font.Font(possible_dir, font_size)
        font = self.__sandbox_action(__get_font,"__get_font(%s,%s)" % (possible_dir, str(font_size)))
        return 0, font

    def get_content(self, name, what_type, **kwargs):
        """
        this will get the content and store on the cache
        but you need to provide the type.

        font_size: case you using fonts.
        """
        font_size   = kwargs.get("font_size") or 12
        force_dir   = kwargs.get("force_dir") or "images/"
        if      what_type == CONTENT_TYPE_IMAGE:    cache_name  = "i_%s" % name
        elif    what_type == CONTENT_TYPE_FONT :    cache_name  = "f%d_%s" % (font_size, name)
        elif    what_type == CONTENT_TYPE_SPRITE:   cache_name  = "s_%s" % name
        else:   return -1
        # -- try to check from the cache --
        if self.cache.get(cache_name):
            self.cache[cache_name][1] += (30 * 1000)
            return self.cache.get(cache_name)[0]
        else:
            # case the cache isn't here for us.
            if what_type == CONTENT_TYPE_IMAGE:
                status, cache_created = self.__get_image_raw(name, use_prefix=force_dir)
                # check if the cache was created (aka, the image)
                if status != 0: return status
                self.cache[cache_name]=[cache_created,pygame.time.get_ticks()+AVG_TIME_IN_CACHE]
                return cache_created
            elif what_type == CONTENT_TYPE_FONT:
                status, cache_created = self.__get_font_raw(name, font_size)
                # check if the font was created (aka, the font)
                if status != 0: return status
                self.cache[cache_name]=[cache_created,pygame.time.get_ticks()+AVG_TIME_IN_CACHE]
                return cache_created
    
    def get_image(self, name, force_dir=None):
        """
        this will return the image, but if there is no image, then the function
        is going to return None, make sure to use get_image_safe() for return a
        'safe' image.
        """
        return self.get_content(name, CONTENT_TYPE_IMAGE, force_dir=force_dir)
    
    def get_sprite(self, name, resolution):
        """
        return the sprite by it's name and it's resolution.
        """
        image_surf = self.get_image(name, force_dir="sprites/")
        if not image_surf:
            return None
        # cut the texture here.
        tex_cut = []
        for y_index in range(0,image_surf.get_height()//resolution):
            for x_index in range(0,image_surf.get_width()//resolution):
                cuten_surface = pygame.Surface((resolution,resolution),pygame.SRCALPHA)
                cuten_surface.blit(image_surf,(-(x_index*resolution),-(y_index*resolution)))
                tex_cut.append(cuten_surface)
        # NOTE: keep this debug for the next versions and forever.
        # this will debug for the future advanced sprite mapper.
        self.debug.write("sprite %s (cut in %d) resulted in %d surfaces" % (
            name, resolution, len(tex_cut)
        ))
        return tex_cut
        
    def get_font(self, name, size):
        """
        this will return a font, but if there is no font, then it will return
        None.
        """
        return self.get_content(name, CONTENT_TYPE_FONT, font_size=size)
    
    def get_content_by_spec(self, spec):
        """
        return the element given by a specification, like:
        {'type':'image','name':'my_image',res:128}
        """
        type_content = spec.get('type')
        name_content = spec.get('name')
        reso_content = spec.get('res') or 64
        # show some debug message here
        self.debug.write("providing by spec: %s" % str(spec))
        # decide what to return
        if type_content == CONTENT_TYPE_NAME_IMAGE:
            # TODO: also, implement a key to decide when the image is
            # to exported as safe or not.
            return self.get_image(name_content)
        elif type_content == CONTENT_TYPE_NAME_SPRITE:
            return self.get_sprite(name_content, reso_content)