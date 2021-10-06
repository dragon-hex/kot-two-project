# as like all the modules, import pygame
import pygame
# import some other modules
from time import gmtime, strftime
import os

# -- begin content storage & provider class:
# provides a image or some asset for the game
# and keeps it in memory.

CONTENT_TYPE_IMAGE      = 1
CONTENT_TYPE_FONT       = 2
CONTENT_TYPE_NAME_IMAGE = 'image'
CONTENT_TYPE_NAME_SPRITE= 'sprite'
CONTENT_TYPE_NAME_FONT  = 'font'

# list of possible errors
RESOURCE_NOT_FOUND      = -1
ERROR_OPENING_RESOURCE  = -2

# some constants (that can be changed on the init)
AVG_TIME_IN_CACHE       = 30 * 1000
DEBUG_CORE              = True

class content:
    def __init__(self):
        # keep on the cache some stuff
        # for a determined amount of time.
        self.__output           = None
        self.__output_enabled   = False
        self.game_path          = None
        self.cache              = {
            # CACHE STORE: <NAME_CACHE_REF>: [<CACHE_DATA>, <LIFESPAN_TIME>]
            # NOTE: -1 is permanent on the cache.
            'null': [0, -1]
        }
    
    def __handle_exception(self, at, exception):
        """ if you hooked a function to the listener... """
        # TODO: finish this.
        pass

    def __get_timestamp(self):
        """ return the time written something (function mostly used by the log function) """
        return strftime("%Y/%m/%d %H:%M:%S",gmtime())
    
    def __write_log(self, the_log):
        """ write some log to the output. """
        if self.__output_enabled:
            text = "(%s) content-provider: %s" % (self.__get_timestamp(),the_log)
            if DEBUG_CORE:
                # NOTE: this is right, we want to know if some problem
                # happen during the write time.
                self.__output.write(text+"\n")
            else:
                try:
                    self.__output.write(text+"\n")
                except Exception as E:
                    self.__handle_exception("__write_log()",E)
    
    def __sandbox_action(self, function, function_name):
        """ function to make the functions smaller, dummi. """
        if DEBUG_CORE:
            return function()
        else:
            try:
                return function()
            except Exception as E:
                self.__handle_exception(function_name,E)

    def __get_image_raw(self, name, use_prefix=None):
        """ try to import the image and all the stuff """
        possible_dir    = self.game_path + (use_prefix or "images/") + name + ".png"
        self.__write_log("providing content for image: %s" % possible_dir)
        if not os.path.exists(possible_dir):
            return RESOURCE_NOT_FOUND, None
        images = None
        if DEBUG_CORE:
            # NOTE: debug doesn't allow to handle certain crash
            # for better view of the core crashes.
            images = pygame.image.load(possible_dir)
        else:
            try:
                images = pygame.image.load(possible_dir)
            except Exception as E:
                # just in case the function fails to load the image...
                self.__handle_exception("__get_image_raw()",E)
                return ERROR_OPENING_RESOURCE, None
        return 0, images
    
    def __get_font_raw(self, name, font_size):
        """ try to import a new font """
        possible_dir    = self.game_path + "fonts/" + name + ".ttf"
        self.__write_log("providing content for font: %s" % possible_dir)
        if not os.path.exists(possible_dir):
            return RESOURCE_NOT_FOUND, None
        font = None
        if DEBUG_CORE:
            # NOTE: this is the same thing on the other functions
            # that can raise exceptions :-)
            font = pygame.font.Font(possible_dir, font_size)
        else:
            try:
                font = pygame.font.Font(possible_dir, font_size)
            except Exception as E:
                self.__handle_exception("__get_font_raw()",E)
        return 0, font

    
    def get_content(self, name, what_type, **kwargs):
        """
        this will get the content and store on the cache
        but you need to provide the type.

        font_size: case you using fonts.
        """
        print(kwargs.get("font_size"))
        font_size   = kwargs.get("font_size") or 12
        force_dir   = kwargs.get("force_dir") or "images/"
        if what_type == CONTENT_TYPE_IMAGE:  cache_name = "img_%s" % name
        elif what_type == CONTENT_TYPE_FONT: cache_name = "font_%s_%d" % (name, font_size)
        if self.cache.get(cache_name):
            # NOTE: when the cache is used again, put a 30 seconds more in the memory.
            self.cache[cache_name][1] += (30 * 1000)
            return self.cache.get(cache_name)[0]
        else:
            # TODO: compress this function on the future.
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
    
    def get_image(self, name):
        """
        this will return the image, but if there is no image, then the function
        is going to return None, make sure to use get_image_safe() for return a
        'safe' image.
        """
        return self.get_content(name, CONTENT_TYPE_IMAGE)
    
    def get_sprite(self, name, resolution):
        """
        return the sprite by it's name and it's resolution.
        """
        image_surf = self.get_image(name, force_dir="sprites/")
        x_div   = image_surf.get_width()  // resolution
        y_div   = image_surf.get_height() // resolution
        surf_d  = pygame.Surface((resolution, resolution), pygame.SRCALPHA) 
        cuts    = []
        for y_index in range(0,y_div):
            for x_index in range(0, x_div):
                surf_d.blit(
                    image_surf,
                    (resolution * x_index,resolution * y_index)
                )
                cuts.append(surf_d.copy())
        return cuts
        
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
        # decide what to return
        if type_content == CONTENT_TYPE_NAME_IMAGE:
            # TODO: also, implement a key to decide when the image is
            # to exported as safe or not.
            return self.get_image(name_content)
        elif type_content == CONTENT_TYPE_NAME_SPRITE:
            return self.get_sprite(name_content, reso_content)