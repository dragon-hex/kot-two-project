# -- import the modules here --
import os
import time
# -- constants --
KOT_FPS_LOCK = 60
# -- pre phase: basic stuff. --
def panic(string, exception):
    """panic: basically kill the program."""
    print("[panic]: %s\n[panic]: %s" % (string,str(exception)))
    exit(-1)
# -- init phase: import modules --
try:    import pygame
except Exception as E: panic("pygame error",E)
try:    import kot
except Exception as E: panic("kot error",E)
# -- continuous phase: basically everything here. --
class kotInstance:
    #
    # init the class here.
    #
    def __init__(self):
        self.kotSharedCore = None
        self.kotSharedStorage = None
    #
    # loop phase here
    #
    def loop(self):
        clock = pygame.time.Clock()
        while self.kotSharedCore.getRunning():
            eventList = pygame.event.get()
            # -- measure time for tick.
            t0 = time.time()
            self.kotSharedCore.mode[self.kotSharedCore.on_mode][0](eventList)
            self.kotSharedCore.tickTime = time.time() - t0
            # -- measure time for draw.
            t0 = time.time()
            self.kotSharedCore.mode[self.kotSharedCore.on_mode][1]()
            self.kotSharedCore.drawTime = time.time() - t0
            # -- setup the tick (aka FPS lock)
            clock.tick(KOT_FPS_LOCK)
    #
    # init phase here
    #
    def __loadThisDirectory(self):
        """__loadThisDirectory: load the directory, the directory is always
        the ./game directory. If you want to customize it, configure the
        hardcoded value here below."""
        DIRECTORY_SET="./game"
        if os.path.exists(DIRECTORY_SET):
            return (os.path.abspath(DIRECTORY_SET)+"/")
        else:
            # NOTE: case the core folder of the game is not
            # found, then just crash the game. This is expected
            # to be done.
            return panic("game not found",'no_exception')
    def __preInit(self):
        """__preInit: init the pygame module here."""
        try: pygame.init()
        except Exception as E:
            return panic("pygame init error",E)
    def __initDisplay(self):
        """__initDisplay: init the display."""
        self.kotSharedCore.window.size      = [800, 600]
        self.kotSharedCore.window.caption   = "Kot DEMO"
        self.kotSharedCore.window.windowInit()
    def init(self):
        """init: init all the required modules."""
        self.__preInit()
        # -- init the shared elements such as the storage and core. --
        # the storage saves all the cache of the images and etc.
        self.kotSharedStorage = kot.core.provider.kotSharedStorage(
            self.__loadThisDirectory()  # -> return the directory for the game.
        )
        # core store the running and the modes.
        self.kotSharedCore = kot.core.system.kotSharedCore()
        # -- init the display here --
        # the game display, but NOTE: the display may change
        # during the next update.
        self.__initDisplay()
        # -- init the mode here --
        # the modes are some possible environment that can be
        # isolated from the modes.
        self.cview_mode = kot.core.cview.cview(self.kotSharedCore,self.kotSharedStorage)
        self.cview_mode.init()
        self.mGame = kot.game.kotGame(self.kotSharedCore, self.kotSharedStorage)
        self.mGame.init()
        self.kotSharedCore.mode = [
            [self.mGame.tick, self.mGame.draw],
            [self.cview_mode.tick, self.cview_mode.draw]
        ]
    # quit phase here
    def quit(self):
        pass
# -- init the wrapper here. --
def wrapper():
    kotLaunchedInstance = kotInstance()
    kotLaunchedInstance.init()
    kotLaunchedInstance.loop()
wrapper()