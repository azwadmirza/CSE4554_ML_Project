    def __init__(self, options):
        """
        Initialize a Toil object from the given options. Note that this is very light-weight and
        that the bulk of the work is done when the context is entered.

        :param argparse.Namespace options: command line options specified by the user
        """
        super(Toil, self).__init__()
        self.options = options
        self.config = None
        self._jobStore = None
        self._batchSystem = None
        self._provisioner = None
        self._jobCache = dict()
        self._inContextManager = False