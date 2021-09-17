# use the 'os' for check some directories for the engine
# and use 'sys' for get the python version and the output
# for the corelog.texts (mostly of the time is sys.stdout)
# use 'time' for measure the program execution time, this
# will be used for some games (probably)...
import  os, sys, time

# try to import the most important library, pygame.
try:    
    import pygame
    K2_PYGAME_IMPORTED  = True
except Exception as E:
    K2_PYGAME_IMPORTED  = False
    K2_PYGAME_ERROR     = E

# define some constants here
K2_PYTHON_VERSION   = "%d.%d" % (sys.version_info[0], sys.version_info[1])
K2_INITIAL_TIME     = time.time_ns()
# NOTE: the default output is always a file named
# 'kot-two.log', even if you disable the output.
K2_DEFAULT_OUTPUT   = open('kot-two.log', 'w')
K2_DEFAULT_RESFOLDER= './engine-res/'

# kot2_engine: here is stored the engine.
class kot2_engine:
    def __init__(self):
        """ here is the whole engine. """
        self.root_path  = self.__load_core_path()
    def __crash(self, string):
        """
        write on the crash.
        """
        K2_DEFAULT_OUTPUT.write("crash: %s\n" % string)
        K2_DEFAULT_OUTPUT.close()
        return exit(1)
    def __crash_with_error(self, string, error):
        """ crash but with a error (exception) """
        K2_DEFAULT_OUTPUT.write("crash exception: %s" % str(error))
        self.__crash(string)
    def __log(self, string):
        """ write log on the file """
        K2_DEFAULT_OUTPUT.write("kot2_engine: %s\n" % string)
    def __load_core_path(self):
        """
        load the core path for the game. The core path is always checked to be ./
        and it's always a folder called 'engine-res' the 'engine-res' folder will 
        contain the minimal stuff for the engine menu and the engine library.
        """
        if os.path.isdir(K2_DEFAULT_RESFOLDER):
            self.__crash('could not open the folder.')
        # TODO: check integrity.
        return K2_DEFAULT_RESFOLDER
    def __init_pygame(self):
        """ init the pygame library """
        if not K2_PYGAME_IMPORTED:
            self.__crash_with_error("couldn't import pygame", K2_PYGAME_ERROR)
        pygame.init()
    def run(self):
        """
        execute a series of code functions to make
        the engine run.
        """
        self.__init_pygame()

# kot2_wrapper: the wrapper can only run it as main
# and can't run as library
if __name__ == '__main__':
    kot2_engine().run()
else:
    raise ImportError("module '%s' is not exportable." % __name__)