# check for pygame
try:    import pygame 
except Exception as E:
    # TODO: do something to the error.
    exit(
        print("'pygame' couldn't be imported: %s" % str(E))
    )
# and finally check for kot2
try:    import kot2
except Exception as E:
    # TODO: do something to the error
    exit(
        print("'kot2' couldn't be imported: %s" % str(E))
    )
# -- begin the wrapper class
class kot2_wrapper:
    def __init__(self):
        self.game_core = kot2.engine.core.game_core()
        self.