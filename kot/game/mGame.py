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
        self.kotViewportPosition = [0, 0]
        self.kotWorlds = None
        # -- control some internal events --

    #
    # -- events from the game --
    #
    def __atWorldUpdate(self):
        """__atWorldUpdate: this will show the title card."""
        pass

    #
    # -- init region --
    #
    def initViewport(self):
        """initViewport: the viewport is what the name sugests, it generates
        a screen sized buffer."""
        pass
    
    def initWorlds(self):
        """initWorlds: init the worlds."""
        self.kotWorlds = kotWorld(self.kotSharedCore, self.kotSharedStorage, self.kotSharedCore.window.surface.get_size())
        self.kotWorlds.atWorldUpdate = lambda: self.__atWorldUpdate()
        self.kotWorlds.init()

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
    
    def videoResizeEvent(self, newSizeX, newSizeY):
        """videoResizeEvent: this will automatically reconfigurate the entire
        game, like updating the screen size, etc."""
        self.kotSharedCore.window.size = [newSizeX, newSizeY]
        self.kotSharedCore.window.windowUpdateProperties()

    def tick(self, eventList):
        """tick: tick the game events."""
        for event in eventList:
            if event.type == pygame.QUIT:
                self.__atQuit()
            if event.type == pygame.VIDEORESIZE:
                self.videoResizeEvent(event.w, event.h)

        # ticks
        self.coreUI.tick(eventList)             # tick the core GUI
        self.__updateDebugGui()                 # tick the DEBUG GUI
        self.performSubroutines()               # perform subroutines.
        self.kotWorlds.tick(eventList)          # and finally tick the world

    #
    # -- draw region --
    #
    def updateViewport(self):
        """updateViewport: basically update the viewport.""" 
        self.kotSharedCore.window.surface.blit(self.kotWorlds.viewport,self.kotViewportPosition)
    
    def drawWorldCard(self):
        """showWorldCard: shows the world icon + name."""
        pass

    def draw(self):
        """draw: draw everything that is need on the screen."""
        # NOTE: the GUI is always above the world.
        self.kotWorlds.draw()
        # update the viewport on the screen
        self.updateViewport()
        self.coreUI.draw()
        pygame.display.flip()