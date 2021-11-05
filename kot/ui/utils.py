def getAbsolutePositionByPercents(self, targetSurfaceSize, targetObjectSize, xPorcent, yPorcent):
    """getAbsolutePositionByPercents: return the actual position on the screen
    of such object using the percent position set."""
    targetSurfaceSizeX = targetSurfaceSize[0]
    targetSurfaceSizeY = targetSurfaceSize[1]
    targetObjectSizeX  = targetObjectSize[0]
    targetObjectSizeY  = targetObjectSize[1]
    # how much positions can it set before ending?
    
