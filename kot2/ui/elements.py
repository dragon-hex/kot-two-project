# import the project modules here
import pygame
import kot2.util
import sys

# import the base module 
from . import base

# define some project constants.
DEBUG_THIS_FILE     = True

class __content_pool:
    """ 
    This is common element store and tick functions, this
    class is shared between the classes display and frames.
    """
    def __init__(self, **kwargs):
        """
        error_hook: the error hook is a function to be called
        when a error happens during some program execution.
        """
        self.error_hook = kwargs.get("error_hook")
        self.elements   = []
    
    def __hook_error(self, on_function, exception):
        """ get the error and call the hook. """
        try:
            self.error_hook(on_function,  exception)
        except:
            pass

    def tick_element(self, ev_list):
        """
        tick the element list here.
        """
        for element in self.elements:
            if DEBUG_THIS_FILE:
                element.tick(ev_list)
            else:
                try:
                    element.tick(ev_list)
                except Exception as E:
                    self.__hook_error("tick", E)
    
    def draw_element(self):
        """
        draw the element list here.
        """
        for element in self.elements:
            if DEBUG_THIS_FILE:
                element.draw()
            else:
                try:
                    element.draw()
                except Exception as E:
                    self.__hook_error("draw", E)
    
    def insert_element(self, element):
        """
        insert the element.
        """
        self.elements.append(element)

# -- build the style --
class style:
    def __init__(self):
        """ some cool styles. """
        self.visible    = True

# -- display class begin here --
class cursor:
    def __init__(self):
        # CURSOR RECT & COLLISION
        self.cursor_rect = None

        # CURSOR APPEARS?
        self.cursor_visible = True

        # CURSOR TEXTURING
        self.cursor_textures        = []
        self.cursor_state           = 0
        self.cursor_animation_index = 0
        self.cursor_animation_time  = 0

        # PROPORTIONS
        self.cursor_size = [32, 32]

        # MAKE DUMMY SQUARE
        self.__make_dummy_square()
    
    def __make_dummy_square(self):
        """ this prevents the game from crashing when there is no sprite. """
        dummy_texture = pygame.Surface((32,32))
        self.cursor_textures = [
            [dummy_texture.copy()],
            [dummy_texture.copy()]
        ]
        self.cursor_rect = pygame.Rect((32, 32),(0, 0))
       
    def __load_position(self):
        """ load the position here """
        self.cursor_rect.x, self.cursor_rect.y = pygame.mouse.get_pos()
        self.cursor_rect.x -= self.cursor_size[0] // 2
        self.cursor_rect.y -= self.cursor_size[1] // 2
        # NOTE: this is just to prevent the cursor from blocking the
        # normal gameplay, in a nutshell, this function will stop the
        # cursor from appearing when playing.

    def tick(self): 
        """ tick the cursor for update it animation and time. """
        if self.cursor_animation_time < pygame.time.get_ticks():
            if len(self.cursor_textures[self.cursor_state]) <= self.cursor_animation_index + 1:
                self.cursor_animation_index = 0
            else:
                self.cursor_animation_index += 1
            self.cursor_animation_time = pygame.time.get_ticks() + (0.5 * 1000)
        self.__load_position()

class display(__content_pool):
    def __init__(self, at_surface):
        """ set the display here. """
        # pre-init the content pool here
        super().__init__()
        # alright, keep __init__ here.
        self.at_surface = at_surface
        self.style = style()
        self.cursor = cursor()
    
    def tick(self, ev_list):
        """ tick the elements on the screen. """
        if self.style.visible:
            self.cursor.tick()
            self.tick_element(ev_list)
    
    def __draw_cursor(self):
        """ draw the cursor on the screen """
        if self.cursor.cursor_visible:
            self.at_surface.blit(
                self.cursor.cursor_textures[self.cursor.cursor_state][self.cursor.cursor_animation_index],
                self.cursor.cursor_rect
            )
    
    def draw(self):
        """ draw the elements on the screen """
        if self.style.visible:
            self.draw_element()
            self.__draw_cursor()
        
# -- frame class begin here --
class frame(__content_pool):
    """
    frame: stores objects inside it, also, it can have
    a background.
    """
    def __init__(self, at_display):#
        # pre-init the class to the content pool.
        super().__init__()
        # keep the __init__ here :)
        self.type = "frame"
        self.style = style()
        self.background = None
        self.background_pos = None
    
    def new_background(self, background_size):
        """ generate a new background. """
        self.background = pygame.Surface(background_size, pygame.SRC_ALPHA)
    
    def tick(self, ev_list):
        """ tick all the elements on the list. """
        if self.style.visible:
            self.tick_element(ev_list)
    
    def draw(self):
        if self.style.visible:
            self.draw_element()
