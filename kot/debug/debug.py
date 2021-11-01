from time import strftime, gmtime
class kotDebug:
    def __init__(self, output=None, logFrom='unknown'):
        """kotDebug: store the debug system."""
        self.output = output
        self.name = logFrom
        self.logIndex = 0
        self.enabled = True
    def __get_timestamp(self):
        """ return a common timestamp. """
        return strftime("%Y/%m/%d %H:%M:%S",gmtime())
    def write(self, string):
        """write: write all your log!"""
        if self.enabled:
            self.output.write("[time = '%s'] from = %s, log_index = 0x%0.4d: %s\n" %(
                self.__get_timestamp(),     # -> return the time;
                self.name,                  # -> the package name;
                self.logIndex,              # -> the message index;
                string                      # -> and finally the string.
            ))