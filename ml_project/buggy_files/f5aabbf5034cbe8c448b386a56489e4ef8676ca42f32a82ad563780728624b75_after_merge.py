    def __singleton_init__(
        self,
        opts,
        functions,
        returners=None,
        intervals=None,
        cleanup=None,
        proxy=None,
        standalone=False,
        utils=None,
        _subprocess_list=None,
    ):
        self.opts = opts
        self.proxy = proxy
        self.functions = functions
        self.utils = utils or salt.loader.utils(opts)
        self.standalone = standalone
        self.skip_function = None
        self.skip_during_range = None
        self.splay = None
        self.enabled = True
        if isinstance(intervals, dict):
            self.intervals = intervals
        else:
            self.intervals = {}
        if not self.standalone:
            if hasattr(returners, "__getitem__"):
                self.returners = returners
            else:
                self.returners = returners.loader.gen_functions()
        try:
            self.time_offset = self.functions.get(
                "timezone.get_offset", lambda: "0000"
            )()
        except Exception:  # pylint: disable=W0703
            # get_offset can fail, if that happens, default to 0000
            log.warning(
                "Unable to obtain correct timezone offset, defaulting to 0000",
                exc_info_on_loglevel=logging.DEBUG,
            )
            self.time_offset = "0000"

        self.schedule_returner = self.option("schedule_returner")
        # Keep track of the lowest loop interval needed in this variable
        self.loop_interval = six.MAXSIZE
        if not self.standalone:
            clean_proc_dir(opts)
        if cleanup:
            for prefix in cleanup:
                self.delete_job_prefix(prefix)
        if _subprocess_list is None:
            self._subprocess_list = salt.utils.process.SubprocessList()
        else:
            self._subprocess_list = _subprocess_list