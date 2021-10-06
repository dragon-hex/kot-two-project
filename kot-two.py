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
        # pre-init the content provider
        self.content.game_path = self.__get_game_path()
        # init the game shared resources
        self.game_core.init_core(self.__load_initial_info())
        self.game_core.running = True
        # post initialization of the game core
        self.game_core.post_init(self.content)
        # init the main game
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
    def panic(self, initialized_at, reason='unknown.'):
        """ oopsie, show the message to quit the game, this is a 'sub-mode'
            inside the game wrapper, for the mostly of the time, you need to
            write your own 'panic' screen. This screen only works if the 
            display is initialized though. """
        # TODO: optimize this function to occupy less lines.
        # some functions here
        def __get_random_secret_message():
            """ return the classical message for errors. """
            import random as __random
            phrases = [
                "Oh no!",
                "Well... too bad for me.",
                "Sadly, It wasn't too bad.",
                "The crash... is a lie!",
                "red pila.",
                "Doing it online now guys!",
                "Juseba, que poxa é essa?",
                "Hello! I'm Kot2 and I'm crashy!",
                "I lost my mind!",
                "Insanity is... me! >:)",
                "There is a pile of useless information in me.",
                "Python Snake is too good.",
                "Python Snake is not too good.",
                "Python Snake just bite me!",
                "Pygame? more like...",
                "Your computer didn't like me.",
                "I promise, I'm not copying the cave game.",
                "Why don't you stalk this error? wait... no!",
                "There is nothing to see here.",
                "Boo! I'm a creepy ghost!",
                "Keep me in the outside.",
                "1337",
                "Meet my girlfriend, GlaDOS! Oh! She is very shy.",
                "Running in less than 10 bytes of memory",
                "john doe",
                "jane doe",
                "saiki psi kusoo man",
                "'Na verdade eu sou assim... (...)'",
                "yo tengo",
                "yo soy miki, hatsuni miki",
                "no hablas espanol",
                "I only say the truth, trust me!"
            ]
            return phrases[__random.randint(0,len(phrases)-1)]
        # do a primitive way to show the stuff, just clean the screen
        # basically, copy the last thing shown and put it to clean the
        # screen itself.
        last_thing_shown = self.game_core.window.surface.copy()
        font = self.content.get_font("normal",16)
        # put some text on the screen
        # TODO: get the project authors and name.
        project_name    = "Kot2-Generic-Project"
        project_author  = "Pipes Studios"
        texts = [
            "Kot-Two Engine has experienced a several CRASH!",
            "'%s'" % __get_random_secret_message(),
            "-" * 80,
            "Project: %s, by: %s" % (project_name, project_author),
            "at: '%s' function, reason: '%s'" % (initialized_at, reason),
            "The game will try to save and then close, click ENTER to proceed."
        ]
        # set the text surface & the project image.
        text_surface = pygame.Surface(self.game_core.window.surface.get_size(),pygame.SRCALPHA)
        text_surface.fill((10,10,100,100))
        # put the project image on the bottom
        x_pos   = text_surface.get_width() - 10
        y_pos   = text_surface.get_height() - 10
        p_image = self.game_core.project_img.copy()
        text_surface.blit(p_image,(x_pos - p_image.get_width(), y_pos - p_image.get_height()))
        # render the list here
        height_set = 0
        for text in texts:
            text_r = font.render(text,True,(0xFF,0xFF,0xFF))
            text_surface.blit(text_r,(0, height_set))
            height_set += text_r.get_height() + 5
        # do the animation to show the text before the loop
        self.game_core.window.surface.blit(last_thing_shown,(0,0))
        self.game_core.window.surface.blit(text_surface,(0, 0))
        # finally render the game icon
        # keep it on loop
        clock = pygame.time.Clock()
        closed = False
        while not closed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    closed = True
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        closed = True
                        break
            pygame.display.flip()
            # NOTE: since this is the display screen for a ERROR
            # keep the clock very low.
            clock.tick(25)
        # TODO: quit the screen and game, but before try to save the player
        # information.
        exit(-1)

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
        # TODO: show the crash also, on possibly the init stage on the future
        # by using tkinter or even QT.
        at_step         = 0
        try:
            self.init()     ; at_step += 1
            self.loop()     ; at_step += 1
            self.quit()     ; at_step += 1
        except Exception as E:
            # TODO: handle more information & update the panic function.
            # case the step was after the init.
            info_handled=E
            if at_step > 0: self.panic(["init","loop","quit"][at_step],reason=info_handled)
            else:
                # if the init has failed to... init(), then
                # just show a missing screen and die.
                print("couldn't init the engine.")
                print(str(E))
                exit(-1)
# -- run the wrapper
def wrapper():
    kot2_wi = kot2_wrapper()
    kot2_wi.run()
wrapper()