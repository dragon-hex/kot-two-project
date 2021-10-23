#
# CONSTS AND MORE
#

CURSOR_NORMAL_STATE     = 0
CURSOR_WAITING_STATE    = 1

# After 10 times inside the loop, hide it.
CURSOR_HIDE_TIME        = 10

#
# Element Styles
#

class generic_shared_prop:
    def __init__(self):
        """ 
        this include things like:
        * visibility
        * locked
        * position
        """
        self.visible    = True
        self.locked     = True
        self.position   = [0, 0]

class label_style(generic_shared_prop):
    def __init__(self):
        """
        this stores the label information about it
        style such as background color and more.
        """
        # load the generic properties.
        super().__init__()
        self.background_color   = (  0,   0,   0)
        self.foreground_color   = (255, 255, 255)
        self.use_antialising    = True