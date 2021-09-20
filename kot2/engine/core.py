import pygame
# -- begin the game_core class:
# the game has a class that is shared everywhere
# across the game called game_core.
class game_window:
    surface     = None
    window_size = [800, 600]
    window_title= "Kot-Two!"
    window_icon = None

    def __install_icon(self):
        """ install a temporary icon or a missing icon """
        import random as __random
        WINDOW_ICON_WIDTH   = 32
        WINDOW_ICON_HEIGHT  = 32
        self.window_icon = pygame.Surface((WINDOW_ICON_WIDTH,WINDOW_ICON_HEIGHT))
        self.window_icon.fill((
            __random.randint(1,255),
            __random.randint(1,255),
            __random.randint(1,255)
        ))

    def init_window(self):
        """ init the window """
        surface = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption(self.window_title)
        if self.window_icon:
            # case the icon is included.
            pygame.display.set_icon(self.window_icon)
        else:
            # install a missing icon.
            self.__install_icon()
            pygame.display.set_icon(self.window_icon)

class game_core:
    window      = game_window()
    def __pygame_init(self):
        """ attempt to init the pygame module """
        # TODO: handle the possible error on pygame init.
        pygame.init()
    
    def __pygame_quit(self):
        """ close the pygame module """
        # TODO: handle some possible error
        pygame.quit()

    def init_core(self):
        """ init the window and the pygame module """
        self.__pygame_init()
        self.window.init_window()
    
    def close_core(self):
        """ close some functions of the core """
        self.__pygame_quit()