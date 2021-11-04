import pygame
import random

class graph:
    def __init__(self, atDisplay, size=[80, 40]):
        # element props
        self.type       = "graph"
        self.display    = atDisplay
        # element proportions and size.
        self.size       = size
        self.pos        = [0, 0]
        self.background = None
        self.graphBuffer= pygame.Surface(self.size,pygame.SRCALPHA)
        self.surface    = pygame.Surface(self.size)
        # style stuff
        self.bgColor    = (0x00, 0x00, 0x00)
        self.fgColor    = (0xFF, 0x00, 0x00)
        # graph setup
        self.averageMax = 60
        self.valueNow   = 0 
        self.lineX      = 0
    
    # -- init region --
    def __renderBackground(self):
        # NOTE: render the background function, but this only
        # rendered when the background is non-existant.
        if not self.background:
            self.background = pygame.Surface(self.size)
            self.background.fill(self.bgColor)
        self.surface.blit(self.background, (0, 0))
    
    def __renderLine(self):
        """__renderLine: the most essential part of the graph."""
        height = random.randint(1,self.size[1])
        # setup the height by the value
        graphSubDivision = self.size[1] / self.averageMax
        height = (graphSubDivision * self.valueNow)
        print(graphSubDivision, height, self.valueNow)
        # draw the line here.
        pygame.draw.line(self.graphBuffer,self.fgColor,(self.lineX,self.size[1]),(self.lineX,self.size[1]-height))
        if self.lineX + 1 > self.size[0]:
            self.graphBuffer.fill((0, 0, 0, 0))
            self.lineX = 0
        else: 
            self.lineX += 1
        self.surface.blit(self.graphBuffer,(0, 0))

    def render(self):
        # render the background.
        self.__renderBackground()
        self.__renderLine()
    
    # -- setup the core --
    def set(self, what):
        self.valueNow = what

    # -- tick region --
    def tick(self, eventList):
        """tick: process the events."""
        # render the line & background.
        self.render()

    # -- draw region --
    def draw(self):
        """draw: put the object on the surface."""
        self.display.atSurface.blit(self.surface, self.pos)