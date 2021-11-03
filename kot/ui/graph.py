import pygame

class graph:
    def __init__(self, atDisplay):
        # element props
        self.type       = "graph"
        self.display    = atDisplay
        # element proportions and size.
        self.size       = [80, 40]
        self.background = None
        # style stuff
        self.bgColor    = (0x00, 0x00, 0x00)
        self.fgColor    = (0xFF, 0x00, 0x00)
    
    # -- init region --
    def __renderBackground(self):
        # NOTE: render the background function.
        self.background = pygame.Surface(self.size)
        self.background.fill(self.bgColor)

    def render(self):
        # render the background.
        self.__renderBackground()

    # -- tick region --
    def tick(self, eventList):
        pass

    # -- draw region --
    def draw(self):
        pass