# as like all the modules, import pygame
import pygame
# -- begin content storage & provider class:
# provides a image or some asset for the game
# and keeps it in memory.

CONTENT_TYPE_IMAGE      = 1
CONTENT_TYPE_FONT       = 2

class content:
    def __init__(self):
        # keep on the cache some stuff
        # for a determined amount of time.
        self.game_path      = None
        self.cache          = {
            # CACHE STORE: <NAME_CACHE_REF>: [<CACHE_DATA>, <LIFESPAN_TIME>]
            # NOTE: -1 is permanent on the cache.
            'null': [0, -1]
        }
    
    def get_content(self, name, what_type, **kwargs):
        """
        this will get the content and store on the cache
        but you need to provide the type.

        font_size: case you using fonts.
        """
        font_size   = kwargs.get("font_size") or 12
        if what_type == CONTENT_TYPE_IMAGE:  cache_name = "img_%d" % name
        elif what_type == CONTENT_TYPE_FONT: cache_name = "font_%d_%d" % (name, font_size)
        if self.cache.get(cache_name):
            # NOTE: when the cache is used again, put a 30 seconds more in the memory.
            self.cache[cache_name][1] += (30 * 1000)
            return self.cache.get(cache_name)[0]