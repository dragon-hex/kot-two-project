# import some python modules
import os
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
        self.game_core          = kot2.engine.core.game_core()
        self.content            = kot2.system.content.content()
    def __get_game_path(self):
        """ basically, get the game path """
        return os.path.abspath("./game") + "/"
    def __load_initial_info(self):
        """ the initial game info is found inside the game folder, on the
            index.json file, there is contained the information for the
            window size, title and etc. """
        initial_info = kot2.util.cjson.jsonc_get(self.content.game_path+"index.json")
        return initial_info
    def init(self):
        """ init all things """
        self.content.game_path = self.__get_game_path()
        self.game_core.init_core(self.__load_initial_info())
        self.game_core.running = True
        self.main_game  = kot2.game.world.m_world(self.content,self.game_core)
        self.main_game.init()
        # setup the rooms
        self.game_core.modes = [
            # 1° mode is the game itself
            [self.main_game.tick, self.main_game.draw],
            # 2° mode is the menu
            # 3° mode is the credits
        ]
    def __tick(self, ev_list):
        """ some generic function to update """
        for ev in ev_list:
            if ev.type == pygame.QUIT:
                self.game_core.running = False
                return
    def __draw(self):
        """ some generic function to update """
        pygame.display.flip()
    def loop(self):
        """ keep the game on loop """
        clock = pygame.time.Clock()
        while self.game_core.running:
            # setup the list
            ev_list = pygame.event.get()
            self.game_core.modes[self.game_core.on_mode][0](ev_list)
            self.game_core.modes[self.game_core.on_mode][1]()
            # TODO: allow the player to change the FPS.
            clock.tick(60)
    def quit(self):
        """ basically quit the game """
        self.game_core.close_core()
    def run(self):
        """ run everything """
        self.init()
        self.loop()
        self.quit()
# -- run the wrapper
def wrapper():
    kot2_wi = kot2_wrapper()
    kot2_wi.run()
wrapper()