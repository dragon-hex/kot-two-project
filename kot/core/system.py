# -- import the classes. --
import pygame
# -- kotWindow: stores the window.
class kotWindow:
    def __init__(self):
        self.surface = None
        self.icon = None
        self.caption = None
        self.size = None
    def __applyTheIcon(self):
        """__applyTheIcon: basically applies the window icon."""
        if self.icon:
            try: pygame.display.set_icon(self.icon)
            except: return False
            return True
    def windowSetIcon(self, windowIcon):
        """windowSetIcon: set the window icon."""
        self.icon = windowIcon
        self.__applyTheIcon()
    def windowInit(self):
        """windowInit: initializes the window."""
        self.surface = pygame.display.set_mode(self.size,pygame.RESIZABLE)
        pygame.display.set_caption(self.caption)
        self.__applyTheIcon()
    def windowUpdateProperties(self):
        """windowUpdateProperties: update the window properties."""
        pygame.display.set_caption(self.caption)
        pygame.display.set_mode(self.size,pygame.RESIZABLE)
        self.__applyTheIcon()

class kotSharedCore:
    def __init__(self):
        self.window = kotWindow()
        self.running = True
        self.mode = []
        self.on_mode = 0
        # for the statistics & debug gui's
        self.tickTime = 0
        self.drawTime = 0
    def getRunning(self):
        """getRunning: get the state of the game."""
        return self.running