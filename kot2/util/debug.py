import sys
from time import strftime, gmtime
class debug_instance:
    """
    This is a simple debug output module.
    """
    name_module     = 'unknown'
    output_to       = None
    output_en       = False

    def __get_timestamp(self):
        """ return a common timestamp. """
        return strftime("%Y/%m/%d %H:%M:%S",gmtime())

    def write(self, string):
        """ this function is not async.
            use with responsability! """
        if self.output_en:
            try:
                self.output_to.write("(%s) [%s]: %s\n" % (
                    self.__get_timestamp(),self.name_module,string
                ))
            except:
                # catch some possible errors during the
                # file writting, such as I/O and problems
                # on the hard drive.
                return
