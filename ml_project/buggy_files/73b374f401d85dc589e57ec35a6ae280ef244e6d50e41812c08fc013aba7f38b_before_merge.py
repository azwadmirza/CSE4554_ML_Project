    def __init__(self, processes, *args, **kwargs):
        """
        Args:
        ----
        processes : number of processes to use; must be at least two.
        args : should include `relevant_ids` and `dictionary` (see `UsesDictionary.__init__`).
        kwargs : can include `batch_size`, which is the number of docs to send to a worker at a
                 time. If not included, it defaults to 64.
        """
        super(ParallelWordOccurrenceAccumulator, self).__init__(*args)
        if processes < 2:
            raise ValueError(
                "Must have at least 2 processes to run in parallel; got %d" % processes)
        self.processes = processes
        self.batch_size = kwargs.get('batch_size', 64)