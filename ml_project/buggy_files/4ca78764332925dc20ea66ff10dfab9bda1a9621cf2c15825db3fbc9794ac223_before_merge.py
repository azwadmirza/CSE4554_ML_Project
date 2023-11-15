    def __singleton_init__(self, opts, functions, returners=None, intervals=None, cleanup=None, proxy=None):
        self.opts = opts
        self.proxy = proxy
        self.functions = functions
        if isinstance(intervals, dict):
            self.intervals = intervals
        else:
            self.intervals = {}
        if hasattr(returners, '__getitem__'):
            self.returners = returners
        else:
            self.returners = returners.loader.gen_functions()
        self.time_offset = self.functions.get('timezone.get_offset', lambda: '0000')()
        self.schedule_returner = self.option('schedule_returner')
        # Keep track of the lowest loop interval needed in this variable
        self.loop_interval = six.MAXSIZE
        clean_proc_dir(opts)
        if cleanup:
            for prefix in cleanup:
                self.delete_job_prefix(prefix)