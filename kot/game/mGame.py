# -- import the module --
import os
import pygame


# -- import the world --
from .world import kotWorld
import kot.ui as ui
import kot.debug as debug
from kot.utils.jsonLoader import jsonLoad
import sys

DEBUG_THIS_FILE = True

# -- begin the main view here --
class kotGame:
    def __init__(self, kotSharedCore, kotSharedStorage):
        """kotGame: this is really the game, it will attempt to
        load the save you put. But, first run the menu."""
        self.kotSharedCore = kotSharedCore
        self.kotSharedStorage = kotSharedStorage
        self.kotViewportPosition = [0, 0]
        self.kotWorlds = None
        # setup the debug
        self.debug = debug.kotDebug(output=sys.stdout,logFrom="mGame")
        self.debug.enabled = DEBUG_THIS_FILE

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
        self.debug.write("initialzing the world engine...")
        # init the world engine
        self.kotWorlds = kotWorld(self.kotSharedCore, self.kotSharedStorage)
        self.kotWorlds.atWorldUpdate = lambda: self.__atWorldUpdate()
        self.kotWorlds.init()
        # init the world by the init.json file inside that, in-case it
        # is present.
        __testFile = self.kotSharedStorage.gamePath+"data/init.json"
        self.debug.write("testing for file = %s" % __testFile)
        if os.path.exists(__testFile):
            self.debug.write("found world list! proceeding init...")
            self.proceedInitializingWorldsByList(__testFile)
        else:
            self.debug.write("no world load list found!")
    
    def proceedInitializingWorldsByList(self, fileTarget):
        """<thisFunction>: pre-load the worlds by this list."""
        def exhibitLoadingText(textProgress):
            """this is a simple function to show the progress of the loading."""
            self.kotSharedCore.window.surface.fill((0xFF,0xFF,0xFF))
            __fontRendered = self.kotSharedStorage.getFont("normal",16).render(textProgress,True,(0x00,0x00,0x00))
            self.kotSharedCore.window.surface.blit(
                __fontRendered,
                (
                    0+10,
                    self.kotSharedCore.window.surface.get_height()-__fontRendered.get_height()-10
                )
            )
            # TODO: make this stage process events.
            pygame.display.flip()

        # begin the data extraction here
        data            = jsonLoad(fileTarget)
        dataToLoad      = data.get("initList")
        nDataToLoad     = len(dataToLoad)
        progressDots    = ''
        for dataIndex in range(0,nDataToLoad):
            # load the world -> load the json data -> send to the world builder.
            progressDots    = progressDots+'.' if len(progressDots) < 3 else ''
            worldName       = dataToLoad[dataIndex]
            possiblePath    = self.kotSharedStorage.gamePath+"data/"+worldName+".json"
            worldData       = jsonLoad(possiblePath)
            worldNameFound  = worldData['data']['name']
            # show to debug & screen the stage
            self.debug.write("Loading world (%d/%d)= %s..." % (dataIndex+1,nDataToLoad,worldNameFound))
            exhibitLoadingText("Loading world '%s' (%d/%d)%s" % (worldNameFound,dataIndex+1,nDataToLoad,progressDots))
            # finally load the world (this may take some time.)
            self.kotWorlds.loadWorldByData(worldData)

        # TODO: when the save part be done, remove this.
        loadWorldFirstly = data['loadAtInit']
        self.kotWorlds.changeWorld(loadWorldFirstly)

    # -- mini region: coregui & debugui --
    # NOTE: the debug region has a two small graphs, one for calculate the tick
    # and other to calculate the draw function.
    def initDebugUi(self):
        """initDebugUI: setup the graph to be drawn & additional text."""
        self.debugUITickGraph = ui.graph(self.coreUI)
        self.coreUI.insert(self.debugUITickGraph)
        self.debug.write("debug UI is ready!")

    def initCoreUi(self):
        """initCoreUI: the core UI is a display that holds everything and also the cursor."""
        self.coreUI = ui.display(self.kotSharedCore.window.surface)
        self.debug.write("coreUI is ready!")
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
        self.debugUITickGraph.set((self.kotSharedCore.tickTime+self.kotSharedCore.drawTime)*1000)

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

    def processEvents(self, eventList):
        """processEvents: basically do all the processing stuff."""
        for event in eventList:
            if event.type == pygame.QUIT:
                self.__atQuit()
            if event.type == pygame.VIDEORESIZE:
                self.videoResizeEvent(event.w, event.h)

    def tick(self, eventList):
        """tick: tick the game events."""
        self.processEvents(eventList)

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