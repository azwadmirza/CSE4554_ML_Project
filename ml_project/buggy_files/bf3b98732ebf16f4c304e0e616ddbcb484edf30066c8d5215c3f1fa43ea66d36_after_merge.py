    def __init__(self, ta, stats, run_obj="runtime", par_factor=1):
        """
        Constructor

        Parameters
        ----------
            ta : list
                target algorithm command line as list of arguments
            stats: Stats()
                 stats object to collect statistics about runtime and so on                
            run_obj: str
                run objective of SMAC
        """
        self.ta = ta
        self.stats = stats
        self.run_obj = run_obj
        self.par_factor = par_factor

        self.logger = logging.getLogger(self.__class__.__name__)
        self._supports_memory_limit = False