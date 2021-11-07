# import some necessesary modules.
import pygame
import os
# from kot.
from kot.utils import jsonLoad

# constants
KOT_CACHE_MAX_STORE_TIME    = 30
KOT_CONTENT_TYPE_IMAGE      = 'image'
KOT_CONTENT_TYPE_SPRITE     = 'sprite'

class kotSharedStorage:
    
    def __init__(self, gamePath):
        self.gamePath = gamePath
        self.cacheStorage = {}
        self.debug = None

    #
    # -- cache manager --
    #
    def newCache(self, cacheKey, element, forceForever=False):
        """newCache: stores something on the cache system, it will
        automatically create the time limit for it and everything else."""
        self.cacheStorage[cacheKey] = [
            # 0: stores the element
            element,
            # 1: stores the time limit that it
            # can be stored on the cache, for mostly
            # of the time, it is determined by CACHE_MAX_STORE_TIME.
            (-1 if forceForever else pygame.time.get_ticks() + (1000 * KOT_CACHE_MAX_STORE_TIME))
        ]

    def cleanOldCache(self):
        """cleanOldCache: clean the cache if it is not used."""
        for cacheKey in self.cacheStorage.keys():
            thisCacheTime = self.cacheStorage[cacheKey][1] 
            if pygame.time.get_ticks() >= thisCacheTime and thisCacheTime != -1:
                del self.cacheStorage[cacheKey]
                return

    def isCache(self, cacheKey):
        """isCache: return if the key is avaiable in cache."""
        return self.cacheStorage.get(cacheKey)

    def getCache(self, cacheKey):
        """getCache: basically return a element if it is present on the cache and
        also, update it life time, more you use a element, more it will stay on
        the cache."""
        if self.isCache(cacheKey):
            # don't update the time if the time limit has reached up.
            timeOnCache = self.cacheStorage[cacheKey][1]
            if timeOnCache != -1 and timeOnCache < (1000 * 120):
                self.cacheStorage[cacheKey][1] += (1000 * (KOT_CACHE_MAX_STORE_TIME//2))
            return self.cacheStorage[cacheKey][0]
        else:
            return False

    #
    # -- content provider --
    #
    def getImage(self, name, fromDirectory="images", forceCacheForever=False):
        """getImage: return the image surface.
        fromDirectory: the directory base for the image.
        forceCacheForever: if the image is too important, keep it forever in cache."""
        pathDir     = self.gamePath + fromDirectory + "/" + name + ".png"
        # try to get the element from a possible cache.
        cacheKey    = "image_%s_%s" % (fromDirectory,name)
        fromCache   = self.getCache(cacheKey)
        if fromCache:
            return fromCache
        # if the element is not cached, then load it manually.
        if os.path.exists(pathDir):
            # basically try to load the symbol to the cache.
            image = None
            # now proceed to load the image.
            try: image = pygame.image.load(pathDir)
            except Exception as E:
                # TODO: do error hook.
                return False
            # store in cache and return the image
            self.newCache(cacheKey,image,forceForever=forceCacheForever)
            return image
    
    def getSprites(self, name, ordered=False):
        """getSprites(Ordered): get your sprites in dict to be referenced later
        on, this is very useful in GUIS and other stuff that only requires one
        static image. Or it can be unordered (default) for animations."""
        # NOTE: case you modifying the path to your resources on the game
        # here is to change the sprites direction! it is set to default to
        # sprites/, but you can change it here.
        SPRITE_DIR = "sprites/"
        sourceImage = self.getImage(name,fromDirectory=SPRITE_DIR)
        sourceMap   = jsonLoad(self.gamePath + SPRITE_DIR + name + ".json")
        surfaces    = {} if ordered else []
        for spriteKeys in sourceMap.keys():
            size    = sourceMap.get(spriteKeys)['size']
            cutX    = sourceMap.get(spriteKeys)['cutX']
            cutY    = sourceMap.get(spriteKeys)['cutY']
            # NOTE: assert that all the things are right, such as integers and the size that
            # is a list, this prevents from randomly crashing the game.
            assert  ((cutX != None and isinstance(cutX, int)) and (isinstance(cutY, int) and cutY != None) and 
                    (isinstance(size, list) and size != None)), ("Error while processing sprite %s" % spriteKeys)
            assert  (isinstance(size[0],int) and isinstance(size[1],int)),("Error while processing sprite %s" % spriteKeys)
            # case all the values are well asserted, then keep doing the sprite thing.
            dummySurface = pygame.Surface(size,pygame.SRCALPHA)
            dummySurface.blit(sourceImage,(-cutX, -cutY))
            # create a copy instead of a reference.
            # but NOTE: this will consume a bit of memory, so,
            # don't abuse too much of the sprites.
            if ordered: surfaces[spriteKeys] = dummySurface.copy()
            else: surfaces.append(dummySurface.copy())
        return surfaces
    
    def getFont(self, fontName, fontSize):
        """getFont: return the font object."""
        # NOTE: all the fonts should be ended with the extension .dat
        # TODO: create better ways to find the font by it extension.
        FONT_PATH_DEFAULT = "fonts/"
        fontPath    = self.gamePath + FONT_PATH_DEFAULT + fontName + ".dat"
        cacheKey    = "font_%s:%d" % (fontName, fontSize)
        fromCache   = self.getCache(cacheKey)
        if not fromCache:
            # then load the font from the disk.
            font = None
            try: font = pygame.font.Load(fontPath)
            except Exception as E:
                # TODO: make a error hook here.
                return False
            self.newCache(cacheKey,font)
            return font
        else:
            return fromCache
    
    # 
    # -- user data request --
    # 

    def getContentBySpecification(self, whatData, ordered=False):
        """getContentBySpecification: basically gets the content by it specification
        that is used on the JSON files, for example: to get a image with the name of
        'pedro', you would have this configuration: {'name':'pedro','type':'image'}."""
        targetName = whatData['name']       # name of the object
        targetType = whatData['type']       # what the type of the object
        targetSize = whatData.get('size')   # TODO: this will cut and adjust the size for images.
        # assert if the values are correct, this prevent the other functions from crashing
        # and doing some problems on the future.
        # ---
        # TODO: some of the most common mistakes are put names in plural for sprites.
        # so, make a change to the code that allows "sprites" to be a valid answer.
        assert (targetName and (isinstance(targetName,str))),"targetName in Specification is invalid, '%s'" % str(whatData)
        assert (targetType and (isinstance(targetType,str))),"targetType in Specification is invalid, '%s'" % str(whatData)
        assert (targetType in ("image","sprite")),"targetType is '%s', expected: image or sprite." % targetType
        # process the name here.
        if      targetType == KOT_CONTENT_TYPE_IMAGE:
            # TODO: use the getImageSafe(), this function will return a missing texture
            # case the image don't exist and also, it will cut the image to the defined
            # size.
            return self.getImage(targetName)
        elif    targetType == KOT_CONTENT_TYPE_SPRITE:
            # NOTE: This is used more for the trees, it return
            # the array as ordered.
            if ordered:
                return self.getSprites(targetName,ordered=True)
            # TODO: finish the sprite logic for LOCKED sprites
            # and animated sprites from BEGIN to END ranges.
            targetSpriteOnly = whatData.get('only')
            if targetSpriteOnly == None:
                return self.getSprites(targetName)
            else:
                # TODO: return just a image.
                spritesGot = self.getSprites(targetName,ordered=True)
                finalSheet = []
                for sprite in spritesGot.keys():
                    if sprite in targetSpriteOnly:
                        finalSheet.append(spritesGot[sprite])
                return finalSheet