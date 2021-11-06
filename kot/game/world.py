# pygame & random
import pygame
import random

# kot.utils
from kot.utils import jsonLoad

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

KOT_PLAYER_LOOK_UP          = 0
KOT_PLAYER_LOOK_DOWN        = 1
KOT_PLAYER_LOOK_LEFT        = 2
KOT_PLAYER_LOOK_RIGHT       = 3

# -- project modifiers --

# -- the main world stuff --
class kotWorldStorage: 
    def __init__(self):
        # NOTE: this stores the world elements.
        self.name       = "Ajax's Bat Helm"
        self.genericName= "noname"
        # world sections
        self.worldData  = {}
        self.worldElements = {}
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
        self.usingMove  = None

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
        # -- setup the world icon --
        self.worldIcon      = None
        self.worldCard      = None
        # -- the player storage --
        self.playerSize     = None
        self.playerRect     = None
        self.playerTextures = []
        self.playerLookAt   = 1     # NOTE: player is always looking at down (for better view!)
        self.playerTexIndex = 0
        self.playerTexIndexT= 0
        # -- setup event --
        self.atWorldUpdate = None
    
    #
    # -- init stuff phase --
    #
    def init(self):
        """init: init the engine components."""
        self.__initTemporaryPlayerTexture()
        self.__initTemporaryWorld()

    #
    # -- player stuff --
    #
    def __initTemporaryPlayerTexture(self):
        """__initTemporaryPlayerTexture: the game needs a player texture
        at least one for the player, if there is none, the game would crash, so
        this assert the player will have a texture, even though it is just a
        black square."""
        # setup the size, player default size is always 32x32
        # also, the player don't moves but instead, the world,
        # so, the player is always on the center of screen.
        self.playerSize = [32, 32]
        playerPosition  =   [self.viewport.get_width()//2-self.playerSize[0]//2,
                            self.viewport.get_height()//2-self.playerSize[1]//2]
        self.playerRect = pygame.Rect(playerPosition,self.playerSize)
        # the player textures as said before, is just some black
        # squares, later on, it's supposed to be loaded by the world.
        justBlackSquare = pygame.Surface(self.playerSize) ; justBlackSquare.fill((0x00, 0x00, 0x00))
        self.playerTextures = [
            [justBlackSquare.copy()],   # up    direction
            [justBlackSquare.copy()],   # down  direction
            [justBlackSquare.copy()],   # left  direction
            [justBlackSquare.copy()],   # right direction
        ]
        # finish off by setting the position of the player
        # that meaning the direction it is looking.
        self.playerTexIndex = 0
        self.playerTexIndexT = 0
    
    #
    # -- world init --
    #
    def getWorldPath(self, levelName, prefix="level"):
        """getWorldPath: return the world path."""
        return self.kotSharedStorage.gamePath+"data/%s.json"%(prefix+levelName)

    def __loadTemporaryWorld(self):
        """return the level0 world."""
        print(self.getWorldPath("0"))
        return jsonLoad(self.getWorldPath("0"))
        
    def __initTemporaryWorld(self):
        """__initTemporaryWorld: the temporary world is a simple world
        which is a simple block."""
        self.loadWorld(self.__loadTemporaryWorld())

    def loadWorld(self, data):
        """loadWorld: basically load the world and store it on the
        world storage list."""
        # NOTE: create a prototype world class here.
        protoWorld      = kotWorldStorage()
        worldData       = data['data']
        worldBackground = data['world']
        
        # store the sections
        protoWorld.worldData = worldData
        
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
        
        # generate the world elements
        protoWorld.worldElements = data['elements']
        self.loadWorldElements(protoWorld)

        # save the world.
        self.worlds[protoWorld.genericName] = protoWorld
        self.world = self.worlds[protoWorld.genericName]
        self.onWorld = protoWorld.genericName
        
        # low-level configurations
        self.usingMove = self.move
        # NOTE: this is a function to the high level
        # or the world controller, this will make a event
        # on the main game to show the worldCard.
        if callable(self.atWorldUpdate):
            self.atWorldUpdate()
    
    def loadWorldElements(self, world):
        """loadWorldElements: load the world elements, but this will erase
        everything, if you want to load only the texture, see the 
        worldElementTextureRegenerate() function."""
        for element in world.worldElements:
            # NOTE: setup the element name & properties
            # also, the position.
            eName           = element.get("name")
            eGenericName    = element.get("genericName")
            eSize           = element.get("size")
            ePosition       = element.get("position")
            eTexture        = element.get("texture")
            eTextureGot     = self.kotSharedStorage.getContentBySpecification(eTexture)
            print(eTextureGot)
            eTextureType    = (1 if eTexture['type'] == 'sprite' else 0)
            # generate a new element.
            self.newElement(
                world,
                eName=eName,
                eSize=eSize,
                eTexture=eTextureGot,
                eTextureType=eTextureType,
                ePosition=ePosition
            )
    
    def __generateDecorationTrees(self, world):
        """__generateDecorationTrees: this is a internal engine function
        that generate some random trees on your world for demo proporses."""
        listTexturesForTrees    = self.kotSharedStorage.getContentBySpecification(world.tTexture)
        randomGenerator         = random.Random()
        randomGenerator.seed(world.tSeed) 
        # NOTE: the range for tree generation is always 1 to 10.
        # setup the texture index.
        numberForTheTree = randomGenerator.randint(1,10)
        for yIndex in range(0, world.bSize[1]):
            for xIndex in range(0, world.bSize[0]):
                # randomly generate trees.
                generateTree = randomGenerator.randint(1,10)
                if generateTree == numberForTheTree:
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
        worldTileSize   = world.bTileSize
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
    
    def moveTest(self, whatX, whatY):
        """moveTest: basically check what happens if move in some direction."""
        temporaryRectangle = pygame.Rect((self.playerRect.x - whatX, self.playerRect.y - whatY), self.playerSize)
        for element in self.world.elements:
            if element[KOT_ELEMENT_RECT].colliderect(temporaryRectangle):
                return True
        return False

    def move(self, xDir, yDir):
        """move: move the camera + the player."""
        # test for possible collisions.
        if self.moveTest(xDir, yDir):
            return
        # move the world and the elements.
        self.world.camera[0] += xDir
        self.world.camera[1] += yDir
        self.moveElements(xDir, yDir)
    
    def movePrecise(self, xDir, yDir):
        """movePrecise: this is a more expansive move function, this will
        try to move precisely to the max possible direction."""
        maxHitX = 0     ; isXNeg = xDir < 0
        maxHitY = 0     ; isYNeg = yDir < 0
        for hitX in range(0, -(xDir) if isXNeg else xDir):
            if self.moveTest(-hitX if isXNeg else hitX, 0):
                break
            else:
                maxHitX = -hitX if isXNeg else hitX
        for hitY in range(0, -(yDir) if yDir < 0 else yDir): 
            if self.moveTest(0, -hitY if isYNeg else hitY):
                break
            else:
                maxHitY = -hitY if isYNeg else hitY
        # after all this stuff, move the world, case is possible.
        self.world.camera[0] += maxHitX
        self.world.camera[1] += maxHitY
        self.moveElements(maxHitX,maxHitY)
    
    def changePlayerLookAt(self, whatDirection):
        """changePlayerLookAt: changes and process the animation."""
        if whatDirection == self.playerLookAt:
            # if the same direction is set, then don't change, just
            # move to the next index on the animation list (if possible).
            if self.playerTexIndexT <= pygame.time.get_ticks():
                self.playerTexIndex  = (0 if self.playerTexIndex + 1 >= len(self.playerTextures[self.playerLookAt]) else self.playerTexIndex + 1)
                self.playerTexIndexT = pygame.time.get_ticks() + (2 * 1000) 
        else:
            # change the player direction.
            self.playerLookAt = whatDirection
            self.playerTexIndex = 0
            self.playerTexIndexT = 0
    
    def updateWorldElements(self):
        """updateWorldElements: update all the world elements that can
        have a sprite, if it is a image, leave it."""
        for element in self.world.elements:
            if element[KOT_ELEMENT_TEXTURE_TYPE] == 1:
                if element[KOT_ELEMENT_TEXTURE_TINDEX] < pygame.time.get_ticks():
                    spriteListSize = len(element[KOT_ELEMENT_TEXTURE])
                    spriteIndex    = element[KOT_ELEMENT_TEXTURE_INDEX]
                    element[KOT_ELEMENT_TEXTURE_INDEX] = (0 if spriteIndex + 1 >= spriteListSize else (spriteIndex + 1))
                    # TODO: MAKE THE SPRITE HAVE A CUSTOM TIME!
                    element[KOT_ELEMENT_TEXTURE_TINDEX] = pygame.time.get_ticks() + (1 * 1000)


    def tick(self, eventList):
        # NOTE: the move precision is set by the world at the beginning!
        # if you using some action platformer that require a high precision
        # level on the element collisions, please, read the DOC about this
        # mode.
        keyPressed = pygame.key.get_pressed()
        if      keyPressed[KEYS_UP[0]]      or keyPressed[KEYS_UP[1]]:
            self.changePlayerLookAt(KOT_PLAYER_LOOK_UP)
            self.usingMove(0,     self.world.pSpeed)
        elif    keyPressed[KEYS_DOWN[0]]    or keyPressed[KEYS_DOWN[1]]:
            self.changePlayerLookAt(KOT_PLAYER_LOOK_DOWN)
            self.usingMove(0,    -self.world.pSpeed)
        elif    keyPressed[KEYS_LEFT[0]]    or keyPressed[KEYS_LEFT[1]]:
            self.changePlayerLookAt(KOT_PLAYER_LOOK_LEFT)
            self.usingMove(self.world.pSpeed,     0)
        elif    keyPressed[KEYS_RIGHT[0]]   or keyPressed[KEYS_RIGHT[1]]:
            self.changePlayerLookAt(KOT_PLAYER_LOOK_RIGHT)
            self.usingMove(-self.world.pSpeed,    0)
        
        # update the elements (sprites)
        self.updateWorldElements()

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
            if element[KOT_ELEMENT_TEXTURE_TYPE] == 0:
                self.viewport.blit(
                    element[KOT_ELEMENT_TEXTURE],
                    element[KOT_ELEMENT_RECT]
                )
            elif element[KOT_ELEMENT_TEXTURE_TYPE] == 1:
                self.viewport.blit(
                    element[KOT_ELEMENT_TEXTURE][element[KOT_ELEMENT_TEXTURE_INDEX]],
                    element[KOT_ELEMENT_RECT]
                )
    
    def drawPlayer(self):
        """drawPlayer: as the function sugests, it draws the player on
        the viewport."""
        self.viewport.blit(
            self.playerTextures[self.playerLookAt][self.playerTexIndex],
            self.playerRect
        )

    def draw(self):
        """draw: this will draw all the element."""
        self.cleanViewport()
        self.drawBackground()
        self.drawElements()
        self.drawPlayer()