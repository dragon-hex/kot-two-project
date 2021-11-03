class display:
    def __init__(self, atSurface):
        """display: this is the display element, it stores and automatically 
        ticks everything for you! simply and cool B]"""
        self.atSurface = atSurface
        self.elements = []
        
    def insert(self, element):
        """insert: insert a element on the display."""
        self.elements.append(element)

    def tick(self, eventList):
        """tick: tick all the elements and pass the event list."""
        for element in self.elements:
            # TODO: don't leave the function run without in sandbox mode.
            element.tick(eventList)

    def draw(self):
        """draw: well... draw the things on screen."""
        for element in self.elements:
            # TODO: same thing on the tick function.
            element.draw()