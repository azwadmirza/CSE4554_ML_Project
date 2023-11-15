    def __init__(self, specs):
        """
        Parameters
        ----------
        specs : list of SubprocSpec
            Process sepcifications

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
        starttime : floats or None
            Pipeline start timestamp.
        """
        self.starttime = None
        self.ended = False
        self.procs = []
        self.specs = specs
        self.spec = specs[-1]
        self.captured = specs[-1].captured
        self.input = self._output = self.errors = self.endtime = None
        self._closed_handle_cache = {}
        self.lines = []
        self._stderr_prefix = self._stderr_postfix = None
        self.term_pgid = None

        background = self.spec.background
        pipeline_group = None
        for spec in specs:
            if self.starttime is None:
                self.starttime = time.time()
            try:
                proc = spec.run(pipeline_group=pipeline_group)
            except XonshError:
                self._return_terminal()
                raise
            if proc.pid and pipeline_group is None and not spec.is_proxy and \
                    self.captured != 'object':
                pipeline_group = proc.pid
                if update_fg_process_group(pipeline_group, background):
                    self.term_pgid = pipeline_group
            self.procs.append(proc)
        self.proc = self.procs[-1]