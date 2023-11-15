    def defer(self, callable, *args, **kwargs):
        """
        Register a deferred function, i.e. a callable that will be invoked after the current attempt
        at running this job concludes. A job attempt is said to conclude when the job function (or
        the Job.run method for class-based jobs) returns, raises an exception or after the process
        running it terminates abnormally. A deferred function will be called on the node that
        attempted to run the job, even if a subsequent attempt is made on another node. A deferred
        function should be idempotent because it may be called multiple times on the same node or
        even in the same process. More than one deferred function may be registered per job attempt
        by calling this method repeatedly with different arguments. If the same callable is
        registered twice, it will be called twice per job attempt.

        The functions one would typically provide here are cleanup functions that handle
        Toil-external events upon a failure within Toil (killing Docker containers, etc).

        :param function callable: The function to be run after this job.
        :param list args: The arguments to the function
        :param dict kwargs: The keyword arguments to the function
        :return: None
        """
        try:
            getattr(self, 'fileStore')
        except AttributeError:
            raise RuntimeError('A deferred function may only be registered from within the job it '
                               'is being registered with. "%s" was illegally registered.',
                               callable.__name__)
        self.fileStore._registerDeferredFunction(callable, *args, **kwargs)