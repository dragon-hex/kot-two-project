# -- import the module --
import pygame
# -- import the world --
from .world import kotWorld
# -- begin the main view here --
class kotGame:
    def __init__(self, kotSharedCore, kotSharedStorage):
        """kotGame: this is really the game, it will attempt to
        load the save you put. But, first run the menu."""
        self.kotSharedCore = kotSharedCore
        self.kotSharedStorage = kotSharedStorage
        self.kotViewport = None
        self.kotViewportPosition = [0, 0]
        self.kotWorlds = None
    #
    # -- init region --
    #
    def initViewport(self):
        """initViewport: the viewport is what the name sugests, it generates
        a screen sized buffer."""
        self.kotViewport = pygame.Surface(self.kotSharedCore.window.surface.get_size())
    
    def initWorlds(self):
        """initWorlds: init the worlds."""
        self.kotWorlds = kotWorld(self.kotSharedCore, self.kotSharedStorage, self.kotViewport)

    def init(self):
        """init: init everything on the game side."""
        self.initViewport() # init the viewport for the game.
        self.initWorlds()   # init the world control.
    #
    # -- tick region --
    #
    def __atQuit(self):
        """__atQuit: basically quits the game."""
        self.kotSharedCore.running = False

    def tick(self, eventList):
        """tick: tick the game events."""
        for event in eventList:
            if event.type == pygame.QUIT:
                self.__atQuit()
        # tick the world
        self.kotWorlds.tick(eventList)
    
    #
    # -- draw region --
    #
    def updateViewport(self):
        """updateViewport: basically update the viewport.""" 
        self.kotSharedCore.window.surface.blit(self.kotViewport,self.kotViewportPosition)

    def draw(self):
        """draw: draw everything that is need on the screen."""
        self.kotWorlds.draw()
        # update the viewport on the screen
        self.updateViewport()
        pygame.display.flip()