# pygame & random
import pygame
import random
import sys

# kot.utils
from kot.utils import jsonLoad
from kot.debug import kotDebug

# -- keymap --
KEYS_UP         = [pygame.K_UP,     pygame.K_w]
KEYS_DOWN       = [pygame.K_DOWN,   pygame.K_s]
KEYS_RIGHT      = [pygame.K_RIGHT,  pygame.K_d]
KEYS_LEFT       = [pygame.K_LEFT,   pygame.K_a]

KEY_DEBUG_SCREEN            = pygame.K_F3
KEY_DEBUG_ELEMENT_MOVEMENT  = pygame.K_F4

KOT_ELEMENT_NAME            = 0
KOT_ELEMENT_TILE_POSITION   = 1
KOT_ELEMENT_ABS_POSITION    = 2
KOT_ELEMENT_TEXTURE         = 3
KOT_ELEMENT_TEXTURE_TYPE    = 4
KOT_ELEMENT_TEXTURE_INDEX   = 5
KOT_ELEMENT_TEXTURE_TINDEX  = 6
KOT_ELEMENT_RECT            = 7
KOT_ELEMENT_GENERIC_NAME    = 8
KOT_ELEMENT_TEXTURE_DATA    = 9

KOT_PLAYER_LOOK_UP          = 0
KOT_PLAYER_LOOK_DOWN        = 1
KOT_PLAYER_LOOK_LEFT        = 2
KOT_PLAYER_LOOK_RIGHT       = 3

# -- project modifiers --
DEBUG_THIS_FILE             = True

# -- utils --
from .wUtils import *

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
        self.uniqueId   = generateUniqueId()

class kotWorld:
    def __init__(self, kotSharedCore, kotSharedStorage):
        """kotWorld: this is sector responsible for the world generation
        and control, that why it needs the shared cores."""
        # NOTE: if you debugging this file, please read the
        # doc for more information.
        self.debug = kotDebug(output=sys.stdout,logFrom='world')
        self.debug.enabled = DEBUG_THIS_FILE
        # init the shared stuff.
        self.kotSharedCore      = kotSharedCore
        self.kotSharedStorage   = kotSharedStorage
        self.viewport           = pygame.Surface(kotSharedCore.window.surface.get_size())
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
        self.__worldTestElementMovement = False
        self.debug.write("finished to build kotWorld class.")
    
    #
    # -- init stuff phase --
    #
    def init(self):
        """init: init the engine components."""
        self.debug.write("initializing temporary player texture.")
        self.__initTemporaryPlayerTexture()
        self.debug.write("initializing temporary world.")
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
        # debug here
        self.debug.write("player temporary texture generated %s" % str(self.playerSize))
    
    #
    # -- world init --
    #
    def getWorldPath(self, levelName, prefix="level"):
        """getWorldPath: return the world path."""
        return self.kotSharedStorage.gamePath+"data/%s.json"%(prefix+levelName)

    def __loadTemporaryWorld(self, level=0):
        """return the level0 world."""
        level = str(level)
        self.debug.write("temporary level %s" % self.getWorldPath(level))
        return jsonLoad(self.getWorldPath(level))
        
    def __initTemporaryWorld(self):
        """__initTemporaryWorld: the temporary world is a simple world
        which is a simple block."""
        self.loadWorld(self.__loadTemporaryWorld())
        self.loadWorld(self.__loadTemporaryWorld(level=1))

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
            self.debug.write("triggering action for atWorldUpdate.")
            self.atWorldUpdate()
        
    def unloadWorldElements(self, world):
        """unloadWorldElements: remove the world element texture."""
        # remove the old elements.
        self.debug.write("unloading %d elements for world '%s'" % (len(world.elements),world.name))
        for element in world.elements:
            element[KOT_ELEMENT_TEXTURE] = None
        
    def regenerateWorldElements(self, world):
        """regenerateWorldElements: basically load all the elements."""
        self.debug.write("regenerating %d elements for world '%s'" % (len(world.elements),world.name))
        for element in world.elements:
            elementData = element[KOT_ELEMENT_TEXTURE_DATA]
            element[KOT_ELEMENT_TEXTURE] = self.kotSharedStorage.getContentBySpecification(elementData)
    
    # -- past initWorld --

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
            eTextureType    = (1 if eTexture['type'] == 'sprite' else 0)
            # generate a new element.
            self.newElement(
                world,
                eName       =eName,
                eSize       =eSize,
                eTexture    =eTextureGot,
                eTextureType=eTextureType,
                ePosition   =ePosition,
                eGenericName=eGenericName,
                eTextureData=eTexture
            )
            # debug
            self.debug.write("element '%s' was loaded for world '%s'" % (eName, world.name))
    
    def __generateDecorationTrees(self, world):
        """__generateDecorationTrees: this is a internal engine function
        that generate some random trees on your world for demo proporses."""
        self.debug.write("generating decoration trees")
        randomGenerated = random.Random()
        randomGenerated.seed(world.tSeed)
        generateTreeWhen = random.randint(1, 10)
        listTextureOrdered = self.kotSharedStorage.getContentBySpecification(world.tTexture,ordered=True)
        for yIndex in range(0, world.bSize[1]):
            for xIndex in range(0, world.bSize[0]):
                treeKey = randomGenerated.choice(list(listTextureOrdered.keys()))
                if randomGenerated.randint(1, 10) == generateTreeWhen:
                    self.newElement(
                        world,
                        eName="tree-%d-%d" % (xIndex, yIndex),
                        ePosition=[xIndex, yIndex],
                        eSize=[64, 64],
                        eTexture=[listTextureOrdered[treeKey]],
                        eTextureType=1,
                        eGenericName="tree00",
                        eTextureData={'name':world.tTexture['name'],'type':"sprite","only":[treeKey]}
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
        # debug
        self.debug.write("loaded background for world '%s', size: '%s'" % (world.name, str(self.worldBackground.get_size())))
    
    def newElement(self, world, **kwargs):
        """newElement: function to generate a new element on the world.
        --
        keywords:
        eName:          the name of the element to be generated.
        ePosition:      the position of the object in the tiles.
        eSize:          the size of the object.
        eTexture:       the texture for the object.
        eTextureType:   the type of texture used by the element.
        eGenericName:   the generic name of such element.
        eTextureData:   the texture to be regenerated.
        """
        # NOTE: the objects must have a name.
        elementName             = kwargs.get("eName")       ;   assert elementName, "newElement: couldn't find a name."
        elementPosition         = kwargs.get("ePosition")   ;   assert elementPosition, "newElement: couldn't find a position."
        elementSize             = kwargs.get("eSize")       ;   assert elementSize, "newElement: couldn't find the size for element."
        elementTexture          = kwargs.get("eTexture")    ;   assert elementTexture, "newElement: element needs a texture."
        elementTextureType      = kwargs.get("eTextureType")
        elementGenericName      = kwargs.get("eGenericName") or "unknown"
        elementTextureData      = kwargs.get("eTextureData")
        # debug
        self.debug.write("new element being created: %s" % elementName)
        # calculate the position and begin to set the rectangle.
        elementPositionAbsolute = [elementPosition[0] * world.bTileSize, elementPosition[1] * world.bTileSize]
        elementRect             = pygame.Rect((elementPositionAbsolute[0],elementPositionAbsolute[1]),(elementSize[0], elementSize[1]))
        # setup the element here.
        world.elements.append([
            # 0: ELEMENT_NAME: this will store the element's name, on the script language
            # or command, this is very important to identify a element name, for example:
            # getElementByName("spike") -> return element_class<spike>
            elementName,
            # 1: ELEMENT_POSITION: the element initial position, in case of resets, this
            # but the position to be drawn on the screen is on the ELEMENT_RECT, this is
            # just for storage of the initial position!
            elementPosition,
            # 2: ELEMENT_POSITION_ABS: the initial position of the element, this abs position
            # is relative to the background world.
            elementPositionAbsolute,
            # 3: ELEMENT_TEXTURE: the element texture, if sprite is stored inside a list
            # and if it is a image, then it is stored in a single image!
            elementTexture,
            # 4: ELEMENT_TEXTURE_TYPE: the element texture type is what determines the
            # element method to draw.
            elementTextureType,
            # 5: ELEMENT_SPRITE_INDEX: (FOR SPRITES ONLY): this will index the sprite animation.
            0,
            # 6: ELEMENT_SPRITE_INDEX_TIMER: (FOR SPRITES ONLY): this will count the time for the
            # next animation to be set.
            0,
            # 7: ELEMENT_RECT: NOTE: this is the most important element inside the elements,
            # basically this keep the element position & check for collisions.
            elementRect,
            # 8: ELEMENT_GENERIC_NAME: this is mostly of like a generic name for use on the
            # getElementByGenericName("spike.centralspike0") -> return element_class<spike>
            elementGenericName,
            # 9: ELEMENT_GENERIC_DATA: to regenerate the data when the world switch is
            # being set.
            elementTextureData
        ])

    def changeWorld(self, worldKey):
        """changeWorld: change the world to the pointed world."""
        self.debug.write("changing world from %s -> %s" % (self.world.name, worldKey))
        self.unloadWorldElements(self.world)
        self.world = self.worlds[worldKey]
        self.regenerateWorldElements(self.world)
        self.__loadWorldBackground(self.world)
    
    #
    # -- tick the world --
    #
    def moveElements(self, forWorld, xDir, yDir):
        """moveElements: move all the elements."""
        for element in forWorld.elements:
            element[KOT_ELEMENT_RECT].x += xDir
            element[KOT_ELEMENT_RECT].y += yDir
    
    def moveTest(self, whatX, whatY):
        """moveTest: basically check what happens if move in some direction."""
        temporaryRectangle = pygame.Rect((self.playerRect.x - whatX, self.playerRect.y - whatY), self.playerSize)
        for element in self.world.elements:
            if element[KOT_ELEMENT_RECT].colliderect(temporaryRectangle):
                return True
        return False

    def move(self, forWorld, xDir, yDir, disableCollision=False):
        """move: move the camera + the player."""
        # test for possible collisions.
        if not disableCollision:
            if self.moveTest(xDir, yDir):
                return
        # move the world and the elements.
        forWorld.camera[0] += xDir
        forWorld.camera[1] += yDir
        self.moveElements(forWorld, xDir, yDir)
    
    def movePrecise(self, forWorld, xDir, yDir, disableCollision=False):
        """movePrecise: this is a more expansive move function, this will
        try to move precisely to the max possible direction."""
        if not disableCollision:
            maxHitX = 0     ; isXNeg = (xDir < 0)
            maxHitY = 0     ; isYNeg = (yDir < 0)
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
        else:
            maxHitX = xDir
            maxHitY = yDir
        # after all this stuff, move the world, case is possible.
        forWorld.camera[0] += maxHitX
        forWorld.camera[1] += maxHitY
        self.moveElements(forWorld, maxHitX,maxHitY)
    
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
            self.playerLookAt       = whatDirection
            self.playerTexIndex     = 0
            self.playerTexIndexT    = 0
    
    def updateWorldElements(self, world):
        """updateWorldElements: update all the world elements that can
        have a sprite, if it is a image, leave it."""
        for element in world.elements:
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
        for event in eventList:
            if event.type == pygame.KEYDOWN:
                if event.key == KEY_DEBUG_SCREEN:
                    # TODO: this will mostly like to be removed on the last version.
                    # NOTE: it is just to test the multiple worlds that can be loaded.
                    self.changeWorld("level0.lirusekaa" if self.world.genericName != "level0.lirusekaa" else "level-1.lirusekaa")
                if event.key == KEY_DEBUG_ELEMENT_MOVEMENT and DEBUG_THIS_FILE:
                    # TODO: this will mostly like to be removed on the last version.
                    self.__worldTestElementMovement = not self.__worldTestElementMovement
            if event.type == pygame.VIDEORESIZE:
                # trigger all the element resize.
                self.videoResizeEvent(event.w, event.h)

        # 
        # process the keys that are used for movement.
        #
        keyPressed = pygame.key.get_pressed()
        if      keyPressed[KEYS_UP[0]]      or keyPressed[KEYS_UP[1]]:
            self.changePlayerLookAt(KOT_PLAYER_LOOK_UP)
            self.usingMove(self.world, 0,     self.world.pSpeed)
        elif    keyPressed[KEYS_DOWN[0]]    or keyPressed[KEYS_DOWN[1]]:
            self.changePlayerLookAt(KOT_PLAYER_LOOK_DOWN)
            self.usingMove(self.world, 0,    -self.world.pSpeed)
        elif    keyPressed[KEYS_LEFT[0]]    or keyPressed[KEYS_LEFT[1]]:
            self.changePlayerLookAt(KOT_PLAYER_LOOK_LEFT)
            self.usingMove(self.world, self.world.pSpeed,     0)
        elif    keyPressed[KEYS_RIGHT[0]]   or keyPressed[KEYS_RIGHT[1]]:
            self.changePlayerLookAt(KOT_PLAYER_LOOK_RIGHT)
            self.usingMove(self.world, -self.world.pSpeed,    0)
        
        # update the elements (sprites)
        self.updateWorldElements(self.world)
        if self.__worldTestElementMovement:
            self.test_MoveElements()
    
    #
    # -- test functions --
    #

    def test_MoveElements(self):
        """test function (moveElements): this will move the elements
        around the map."""
        movements = [1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6]
        for element in self.world.elements:
            newX = element[KOT_ELEMENT_RECT].x + random.choice(movements)
            if newX > 0 and newX < self.worldBackground.get_size()[0]:
                element[KOT_ELEMENT_RECT].x = newX
            newY = element[KOT_ELEMENT_RECT].y + random.choice(movements)
            if newY > 0 and newY < self.worldBackground.get_size()[1]:
                element[KOT_ELEMENT_RECT].y = newY
    
    #
    # -- video resize event & other subevents --
    #
    
    def RecalculateEverythingResizeEvent(self, prevSize, newSize):
        """vre: videoResizeEvent, this function will recalculate the player
        position, since the player is always on the center, it is very hard
        to check where the old position should be."""
        # NOTE: this worlds like this: calculate the number of spaces that has
        # changed from the last resize.
        newSizeX, newSizeY                      = newSize[0], newSize[1]
        newPlayerPosX, newPlayerPosY            = (newSizeX // 2 - self.playerSize[0] // 2), (newSizeY // 2 - self.playerSize[1] // 2)
        playerOldPos                            = (self.playerRect.x, self.playerRect.y)
        self.playerRect.x, self.playerRect.y    = newPlayerPosX, newPlayerPosY
        posX, posY                              = self.playerRect.x - playerOldPos[0], self.playerRect.y - playerOldPos[1]
        # NOTE: move this world camera & the other worlds
        # this needs to be done because the camera is always on the center.
        for world in self.worlds.keys():
            self.worlds[world].camera[0] += posX
            self.worlds[world].camera[1] += posY
            for element in self.worlds[world].elements:
                element[KOT_ELEMENT_RECT].x += posX
                element[KOT_ELEMENT_RECT].y += posY


    def videoResizeEvent(self, newSizeX, newSizeY):
        """videoResizeEvent: update the viewport and etc."""
        previousViewportSize = self.viewport.get_size() ;   del self.viewport
        self.debug.write("new size for viewport [w = %d, h = %d]" % (newSizeX, newSizeY))
        self.viewport = pygame.Surface((newSizeX, newSizeY))
        self.viewport.fill((0, 0, 0))
        # NOTE: important step, recalculate the world position!
        self.RecalculateEverythingResizeEvent(previousViewportSize,self.viewport.get_size())

    # 
    # -- draw the world --
    #
    def cleanViewport(self):
        """cleanViewport: clean the viewport."""
        self.viewport.fill((0, 0, 0))

    def drawBackground(self):
        """drawBackground: keep the background on the back!"""
        # setup the background.
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
        self.cleanViewport()            # clean the viewport to exhibit the new stuff.
        self.drawBackground()           # draw the background
        self.drawElements()             # & elements
        self.drawPlayer()               # & finally the players.