# -- import the module --
import pygame
# -- import the world --
from .world import kotWorld
import kot.ui as ui
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

    # -- mini region: coregui & debugui --
    # NOTE: the debug region has a two small graphs, one for calculate the tick
    # and other to calculate the draw function.
    def initDebugUi(self):
        """initDebugUI: setup the graph to be drawn & additional text."""
        self.debugUITickGraph = ui.graph(self.coreUI)
        self.coreUI.insert(self.debugUITickGraph)

    def initCoreUi(self):
        """initCoreUI: the core UI is a display that holds everything and also the cursor."""
        self.coreUI = ui.display(self.kotSharedCore.window.surface)
        # init the debug GUI here
        self.initDebugUi()

    def init(self):
        """init: init everything on the game side."""
        self.initViewport() # init the viewport for the game.
        self.initWorlds()   # init the world control.
        self.initCoreUi()   # init the core window.
    #
    # -- tick region --
    #
    def __updateDebugGui(self):
        """__updateDebugGui: setup the GUI for the debug.""" 
        print(self.kotSharedCore.tickTime)
        self.debugUITickGraph.set(self.kotSharedCore.tickTime*1000)

    def __atQuit(self):
        """__atQuit: basically quits the game."""
        self.kotSharedCore.running = False
    
    def __reliefSubRoutine(self):
        """__reliefSubRoutine: some stuff to clean the memory."""
        self.kotSharedStorage.cleanOldCache()

    def performSubroutines(self):
        """performSubroutines: perform some important subroutines."""
        self.__reliefSubRoutine()       # keep the cache memory low as possible.

    def tick(self, eventList):
        """tick: tick the game events."""
        for event in eventList:
            if event.type == pygame.QUIT:
                self.__atQuit()
        # tick the GUI & world.
        # NOTE: the GUI sometimes has more priority due it
        # possibility to change the game during it.
        self.coreUI.tick(eventList)
        self.__updateDebugGui()
        self.kotWorlds.tick(eventList)
        # NOTE: perform the subroutines of the game.

    #
    # -- draw region --
    #
    def updateViewport(self):
        """updateViewport: basically update the viewport.""" 
        self.kotSharedCore.window.surface.blit(self.kotViewport,self.kotViewportPosition)

    def draw(self):
        """draw: draw everything that is need on the screen."""
        # NOTE: the GUI is always above the world.
        self.kotWorlds.draw()
        # update the viewport on the screen
        self.updateViewport()
        self.coreUI.draw()
        pygame.display.flip()