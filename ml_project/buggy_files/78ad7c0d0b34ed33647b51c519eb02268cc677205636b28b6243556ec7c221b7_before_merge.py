    def __init__(self, specs, procs, starttime=None, captured=False):
        """
        Parameters
        ----------
        specs : list of SubprocSpec
            Process sepcifications
        procs : list of Popen-like
            Process objects.
        starttime : floats or None, optional
            Start timestamp.
        captured : bool or str, optional
            Flag for whether or not the command should be captured.

        Attributes
        ----------
        spec : SubprocSpec
            The last specification in specs
        proc : Popen-like
            The process in procs
        ended : bool
            Boolean for if the command has stopped executing.
        input : str
            A string of the standard input.
        output : str
            A string of the standard output.
        errors : str
            A string of the standard error.
        lines : list of str
            The output lines
        """
        self.procs = procs
        self.proc = procs[-1]
        self.specs = specs
        self.spec = specs[-1]
        self.starttime = starttime or time.time()
        self.captured = captured
        self.ended = False
        self.input = self._output = self.errors = self.endtime = None
        self._closed_handle_cache = {}
        self.lines = []
        self._stderr_prefix = self._stderr_postfix = None