    def __init__(self, ta, stats, run_obj="runtime"):
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
        self.logger = logging.getLogger("ExecuteTARun")

        self._supports_memory_limit = False