# import modules
import os, sys
import pygame
import time
# import the kot module
import kot

# -- || -- 

class kotLauncher:
    def __init__(self):
        """ launch everything on the project. """
        self.kotSharedCore      = None
        self.kotSharedStorage   = None

    def __getMainGameFolder(self):
        return os.path.abspath("./game")+"/"

    def __searchInitialProperties(self):
        """searchInitialProperties: setup the initial properties on the
        main project."""
        initialPropertiesJsonData = kot.utils.jsonLoad(self.kotSharedStorage.gamePath+"data/window.json")
        kot.core.provider.buildWindowData(self.kotSharedStorage, initialPropertiesJsonData)
        # -- zz --
        # TODO also setup the initial window size
        self.kotSharedCore.window.size = [800, 600]
        self.kotSharedCore.setupWindowByData(initialPropertiesJsonData)
    
    def __setupModes(self):
        """setupModes: setup the modes here."""
        # setup the core here
        self.kotMainWorld = kot.game.kotGame(self.kotSharedCore, self.kotSharedStorage)
        self.kotMainWorld.init()
        # setup the modes here
        self.kotSharedCore.modes = [
            ["kotMainWorld",    self.kotMainWorld.tick, self.kotMainWorld.draw],
            ["kotNullMode",     None,                   None]
        ]
        self.kotSharedCore.onMode = 0
    
    def __pygameInit(self):
        """pygameInit: init and do the black magic."""
        pygame.init()
    
    def __pygameQuit(self):
        """pygameQuit: quit and do black magic.""" 
        pygame.quit()

    def init(self):
        """init: init the launcher."""
        # init pygame
        self.__pygameInit()
        # init the modules
        self.__pathMainGameDir  = self.__getMainGameFolder()
        self.kotSharedStorage   = kot.core.provider.kotSharedStorage(self.__pathMainGameDir)
        self.kotSharedCore      = kot.core.system.kotSharedCore()
        # prepare to init the window, search the init properties
        self.__searchInitialProperties()
        # setup the window
        self.kotSharedCore.window.windowInit()
        # prepare to init the modes now.
        self.__setupModes()
        self.kotSharedCore.running = True
    
    def loop(self):
        """loop: here is the most important part of the game, the loop part,
        here is called the two functions, .tick() and .draw() of each mode."""
        fpsLock = 60
        clock   = pygame.time.Clock()
        while self.kotSharedCore.running:
            onMode      = self.kotSharedCore.onMode
            eventList   = pygame.event.get()
            # NOTE measure the time of each function
            timeTakenByTick = time.time()
            self.kotSharedCore.modes[onMode][1](eventList)
            timeTakenByTick = time.time() - timeTakenByTick
            timeTakenByDraw = time.time()
            self.kotSharedCore.modes[onMode][2]()
            timeTakenByDraw = time.time() - timeTakenByDraw
            # register on the statistics
            self.kotSharedCore.tickTime = timeTakenByTick
            self.kotSharedCore.drawTime = timeTakenByDraw
            clock.tick(fpsLock)
    
    def quit(self):
        """quit: quit the launcher."""
        self.__pygameQuit()

# -- zz --

def launch():
    kotInstance = kotLauncher()
    kotInstance.init()
    kotInstance.loop()
    kotInstance.quit()

# NOTE launch the project, case is main.
if __name__ == '__main__': launch()