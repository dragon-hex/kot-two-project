from . import base
class label:
    def __init__(self, at_display):
        self.type = "label"
        self.style = base.label_style()
        self.at_display = at_display
        self.font = None
        self.text = None
        # secret variables
        self.__abs_position = [0, 0]
        self.__surface = None
        self.__need_redraw=True
    
    def set_font(self, what_font):
        self.font = what_font
        self.__need_redraw=True
    
    def set_text(self, what_text):
        self.text = what_text
        self.__need_redraw=True
    
    def render(self):
        self.__surface = self.font.render(self.Text,self.style.use_antialising,self.style.foreground_color)
        self.__abs_position = [0, 0]
        self.__need_redraw=False
    
    def tick(self, ev_list):
        # NOTE: tick will also, render the text.
        self.render()

    def draw(self):
        if self.style.visible:
            # NOTE: only draw when the surface is ready.
            if self.__surface:
                self.at_display.at_surface.blit(
                    self.__surface,
                    self.__abs_position
                )