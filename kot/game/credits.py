class kotCredits:
    def __init__(self, kotSharedCore, kotSharedStorage):
        """kotCredits: store the credits here, this is another mode
        of the Kot Project, the kotCredits will read a file inside the
        data folder called 'credits.json', for more info about the
        credits info, read the CREDITS info."""
        # shared stuff here
        self.kotSharedCore = kotSharedCore
        self.kotSharedStorage = kotSharedStorage    