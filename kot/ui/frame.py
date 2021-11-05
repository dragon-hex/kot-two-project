from .const import *
# -- init the frame objects --
class frame:
    def __init__(self, atDisplay):
        """frame: it can store lot of elements, just like a display."""
        # setup the display & background
        self.atDisplay          = atDisplay
        self.background         = None
        # setup the size + position (case you using a background)
        self.usingBackground    = False
        self.size               = [0, 0]
        self.position           = [0, 0]
        # setup the core
        self.__background       = None