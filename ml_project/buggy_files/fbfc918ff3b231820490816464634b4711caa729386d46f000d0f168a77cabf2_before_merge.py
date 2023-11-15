    def __init__(self, dispatcher):
        """
        Init

        :param dispatcher: instance of Dispatcher
        """
        self.dispatcher = dispatcher
        self.loop = dispatcher.loop
        self.bot = dispatcher.bot
        self.storage = dispatcher.storage
        self.applications = []