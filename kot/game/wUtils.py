import random

__uniqueKeysAlreadyGenerated = []
def generateUniqueId(length=64):
    ranges = [
        (ord('a'),ord('z')),
        (ord('A'),ord('Z')),
        (ord('0'),ord('9')),
    ]
    whatId = ""
    while True:
        whatId = ""
        for index in range(0,length):
            whatRange   = random.randint(0,len(ranges)-1)
            rangeSet    = ranges[whatRange]
            whatId      += chr(random.randint(rangeSet[0],rangeSet[1]))
        if whatId in __uniqueKeysAlreadyGenerated:
            continue
        else:
            __uniqueKeysAlreadyGenerated.append(whatId)
            break
    return whatId