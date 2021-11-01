import pygame
import random
# -- keymap --
KEYS_UP         = [pygame.K_UP,     pygame.K_w]
KEYS_DOWN       = [pygame.K_DOWN,   pygame.K_s]
KEYS_RIGHT      = [pygame.K_RIGHT,  pygame.K_d]
KEYS_LEFT       = [pygame.K_LEFT,   pygame.K_a]

KOT_ELEMENT_NAME            = 0
KOT_ELEMENT_TILE_POSITION   = 1
KOT_ELEMENT_ABS_POSITION    = 2
KOT_ELEMENT_TEXTURE         = 3
KOT_ELEMENT_TEXTURE_TYPE    = 4
KOT_ELEMENT_TEXTURE_INDEX   = 5
KOT_ELEMENT_TEXTURE_TINDEX  = 6
KOT_ELEMENT_RECT            = 7

# -- the main world stuff --
class kotWorldStorage: 
    def __init__(self):
        # NOTE: this stores the world elements.
        self.name       = "Ajax's Bat Helm"
        self.genericName= "noname"
        # background is stored here.
        self.bSeed      = 1
        self.bSize      = [0, 0]
        self.bTexture   = None
        self.bTileSize  = 0
        # NOTE: tree decoration section, for more info about the
        # automatic tree decoration, read the documentation!
        self.tTrees     = None
        self.tTexture   = None
        self.tSeed      = 0
        # setup the elements on the world
        self.elements   = []
        # player position & camera.
        self.camera     = [0, 0]
        self.pSpeed     = 4

class kotWorld:
    def __init__(self, kotSharedCore, kotSharedStorage, viewport):
        """kotWorld: this is sector responsible for the world generation
        and control, that why it needs the shared cores."""
        self.kotSharedCore      = kotSharedCore
        self.kotSharedStorage   = kotSharedStorage
        self.viewport           = viewport
        # -- the world storage --
        self.world          = None
        self.worlds         = {}
        self.onWorld        = None
        self.worldBackground= None
        # NOTE: there need a world to be showed case any are loaded.
        self.__initTemporaryWorld()
    
    #
    # -- world init --
    #
    def __initTemporaryWorld(self):
        """__initTemporaryWorld: the temporary world is a simple world
        which is a simple block."""
        self.loadWorld({
            'data': {
                'name'              : "Ajax's Bat Helm",
                'genericName'       : "noname",
            },
            'world': {
                # the 'b' stands for background.
                'bSeed'             : 1,
                'bSize'             : [10, 10],
                'bTexture'          : {'name':"axc_grass0", "type":"sprite", "size":64},
                'bTileSize'         : 64,
                # NOTE: the trees keyword is just a decoration.
                # this is not supposed to be enabled each time.
                'trees'             : True,
                'tTexture'          : {'name':"axc_tree0", "type":"sprite", "size":64},
                'tSeed'             : 0
            },
            'elements': { 

            }
        })
    
    def loadWorld(self, data):
        """loadWorld: basically load the world and store it on the
        world storage list."""
        # NOTE: create a prototype world class here.
        protoWorld      = kotWorldStorage()
        worldData       = data['data']
        worldBackground = data['world']
        # set all the things on the prototype.
        protoWorld.name         = worldData['name']
        protoWorld.genericName  = worldData['genericName']
        # set all the world information.
        protoWorld.bSize = worldBackground['bSize']
        protoWorld.bSeed = worldBackground['bSeed']
        protoWorld.bTexture = worldBackground['bTexture']
        protoWorld.bTileSize = worldBackground['bTileSize']
        # here begin to load the world background
        # the background is generated when the game needs
        # it, so, every time the world changes, the background
        # needs to be regenerated, this is done for
        # save the memory and keep the game memory usage consistent.
        self.__loadWorldBackground(protoWorld)
        # begin to load the world elements, such as tree and
        # other stuff. NOTE: the trees aren't supposed to be
        # load the by the game.
        protoWorld.tTrees       = worldBackground['trees']
        protoWorld.tTexture     = worldBackground['tTexture']
        protoWorld.tSeed        = worldBackground['tSeed']
        protoWorld.elements     = []
        if worldBackground['trees']:
            self.__generateDecorationTrees(protoWorld)
        # save the world.
        self.worlds[protoWorld.genericName] = protoWorld
        self.world = self.worlds[protoWorld.genericName]
        self.onWorld = protoWorld.genericName
    
    def __generateDecorationTrees(self, world):
        """__generateDecorationTrees: this is a internal engine function
        that generate some random trees on your world for demo proporses."""
        listTexturesForTrees    = self.kotSharedStorage.getContentBySpecification(world.tTexture)
        randomGenerator         = random.Random()
        randomGenerator.seed(world.tSeed) 
        # setup the texture index.
        for yIndex in range(0, world.bSize[1]):
            for xIndex in range(0, world.bSize[0]):
                self.newElement(world, 
                    eName="generic.tree00-%d-%d"%(xIndex,yIndex),
                    ePosition=[xIndex,yIndex],
                    eSize=[64, 64],
                    eTexture=random.choice(listTexturesForTrees),
                    eTextureType=0
                )
    
    def __loadWorldBackground(self, world):
        """__loadWorldBackground: load the world background.""" 
        # setup the generator here.
        # NOTE: to create a consistency, this is done by a seed.
        randomGenerator = random.Random()
        randomGenerator.seed(world.bSeed)
        # setup the textures here.
        listTexturesUse = self.kotSharedStorage.getContentBySpecification(world.bTexture)
        worldSize       = world.bSize
        worldTileSize   = world.bTexture['size']
        # generate the surface
        # NOTE: the world supports a possible transparency.
        self.worldBackground    =   pygame.Surface((worldSize[0] * worldTileSize, 
                                    worldSize[1] * worldTileSize),pygame.SRCALPHA)
        # generate the background
        for yIndex in range(0, worldSize[1]):
            for xIndex in range(0, worldSize[0]):
                # select from the list a random texture.
                selectedTexture = randomGenerator.choice(listTexturesUse)
                self.worldBackground.blit(selectedTexture,(
                    worldTileSize * xIndex,
                    worldTileSize * yIndex
                ))
    
    def newElement(self, world, **kwargs):
        """newElement: function to generate a new element on the world.
        --
        keywords:
        eName:          the name of the element to be generated.
        ePosition:      the position of the object in the tiles.
        eSize:          the size of the object.
        eTexture:       the texture for the object.
        eTextureType:   the type of texture used by the element.
        """
        # NOTE: the objects must have a name.
        elementName             = kwargs.get("eName")       ;   assert elementName, "newElement: couldn't find a name."
        elementPosition         = kwargs.get("ePosition")   ;   assert elementPosition, "newElement: couldn't find a position."
        elementSize             = kwargs.get("eSize")       ;   assert elementSize, "newElement: couldn't find the size for element."
        elementTexture          = kwargs.get("eTexture")    ;   assert elementTexture, "newElement: element needs a texture."
        elementTextureType      = kwargs.get("eTextureType")
        # calculate the position and begin to set the rectangle.
        elementPositionAbsolute = [elementPosition[0] * world.bTileSize, elementPosition[1] * world.bTileSize]
        elementRect             = pygame.Rect((elementPositionAbsolute[0],elementPositionAbsolute[1]),(elementSize[0], elementSize[1]))
        # setup the element here.
        world.elements.append([
            # 0: element name
            elementName,
            # 1: element position
            elementPosition,
            # 2: element position (absolute)
            elementPositionAbsolute,
            # 3: elementTexture: stores the element texture.
            # NOTE: even if the texture is a image, it needs to be inside a list!
            elementTexture,
            # 4: elementTextureType: the type of texture to be used, 0: image, 1: sprite.
            elementTextureType,
            # 5: elementTextureIndex (for sprites only): it will index the animation in
            # the sprite list.
            0,
            # 6: elementTextureTimeIndex (for sprites only): it will index the time for the
            # next animation to appear.
            0,
            # 7: elementRect: for collision and etc.
            elementRect
        ])
    
    #
    # -- tick the world --
    #
    def moveElements(self, xDir, yDir):
        """moveElements: move all the elements."""
        for element in self.world.elements:
            element[KOT_ELEMENT_RECT].x += xDir
            element[KOT_ELEMENT_RECT].y += yDir

    def move(self, xDir, yDir):
        """move: move the camera + the player."""
        self.world.camera[0] += xDir
        self.world.camera[1] += yDir
        self.moveElements(xDir, yDir)

    def tick(self, eventList):
        # get the continuous events.
        keyPressed = pygame.key.get_pressed()
        if      keyPressed[KEYS_UP[0]]      or keyPressed[KEYS_UP[1]]:
            self.move(0,     self.world.pSpeed)
        elif    keyPressed[KEYS_DOWN[0]]    or keyPressed[KEYS_DOWN[1]]:
            self.move(0,    -self.world.pSpeed)
        elif    keyPressed[KEYS_LEFT[0]]    or keyPressed[KEYS_LEFT[1]]:
            self.move(self.world.pSpeed,     0)
        elif    keyPressed[KEYS_RIGHT[0]]   or keyPressed[KEYS_RIGHT[1]]:
            self.move(-self.world.pSpeed,    0)

    # 
    # -- draw the world --
    #
    def cleanViewport(self):
        """cleanViewport: clean the viewport."""
        self.viewport.fill((0, 0, 0))

    def drawBackground(self):
        """drawBackground: keep the background on the back!"""
        self.viewport.blit(self.worldBackground,self.world.camera)
    
    def drawElements(self):
        """drawElements: draw the world elements."""
        for element in self.world.elements:
            self.viewport.blit(
                element[KOT_ELEMENT_TEXTURE],
                element[KOT_ELEMENT_RECT]
            )

    def draw(self):
        """draw: this will draw all the element."""
        self.cleanViewport()
        self.drawBackground()
        self.drawElements()