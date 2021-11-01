import pygame
# -- cview: basically a mode to see the installed textures. --
class cview:
    def __init__(self, kotSharedCore, kotSharedStorage):
        # init the window.
        self.kotSharedCore = kotSharedCore
        self.kotSharedStorage = kotSharedStorage
    def init(self):
        self.myImage = self.kotSharedStorage.getSprites("axc_tree0")[0]
    def __atQuit(self):
        """__atQuit: quit the view here by the user."""
        self.kotSharedCore.running = False
    def tick(self, eventList):
        """tick: tick the screen here."""
        for event in eventList:
            if event.type == pygame.QUIT:
                self.__atQuit()
    def draw(self):
        """draw: draw the screen here."""
        self.kotSharedCore.window.surface.blit(self.myImage,(0,0))
        pygame.display.update()