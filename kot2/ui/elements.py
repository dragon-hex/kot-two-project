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
        self.visible    = False

# -- display class begin here --
class cursor:
    def __init__(self):
        self.cursor_textures = []
        self.cursor_state = 0
        self.cursor_animation_index = 0
        self.cursor_animation_time = 0
    
    def tick(self): 
        """ tick the cursor for update it animation and time. """
        if self.cursor_animation_time < pygame.time.get_ticks():
            if len(self.cursor_textures[self.cursor_state]) < self.cursor_animation_index + 1:
                self.cursor_animation_index     = 0
            else:
                self.cursor_animation_index     += 1
            self.cursor_animation_time = pygame.time.get_ticks() + (0.5 * 1000)

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
