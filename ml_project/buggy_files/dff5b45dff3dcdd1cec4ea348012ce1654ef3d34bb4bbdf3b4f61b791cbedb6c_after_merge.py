    def __init__(self, options):
        """
        Initialize a Toil object from the given options. Note that this is very light-weight and
        that the bulk of the work is done when the context is entered.

        :param argparse.Namespace options: command line options specified by the user
        """
        super(Toil, self).__init__()
        self.options = options
        self.config = None
        """
        :type: toil.common.Config
        """
        self._jobStore = None
        """
        :type: toil.jobStores.abstractJobStore.AbstractJobStore
        """
        self._batchSystem = None
        """
        :type: toil.batchSystems.abstractBatchSystem.AbstractBatchSystem
        """
        self._provisioner = None
        """
        :type: toil.provisioners.abstractProvisioner.AbstractProvisioner
        """
        self._jobCache = dict()
        self._inContextManager = False