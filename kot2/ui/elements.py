# import the project modules here
import pygame
import kot2.util
import sys

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
class display(__content_pool):
    def __init__(self, at_surface):
        """ set the display here. """
        self.at_surface = at_surface
        # some custom properties
        self.style = style()
    
    def tick(self, ev_list):
        """ tick the elements on the screen. """
        if self.style.visible:
            self.tick_element(ev_list)
    
    def draw(self):
        """ draw the elements on the screen """
        if self.style.visible:
            self.draw_element()
        
# -- frame class begin here --