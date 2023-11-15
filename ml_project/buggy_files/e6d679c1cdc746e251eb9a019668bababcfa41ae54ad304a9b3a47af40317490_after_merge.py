    def defer(self, function, *args, **kwargs):
        """
        Register a deferred function, i.e. a callable that will be invoked after the current
        attempt at running this job concludes. A job attempt is said to conclude when the job
        function (or the :meth:`Job.run` method for class-based jobs) returns, raises an
        exception or after the process running it terminates abnormally. A deferred function will
        be called on the node that attempted to run the job, even if a subsequent attempt is made
        on another node. A deferred function should be idempotent because it may be called
        multiple times on the same node or even in the same process. More than one deferred
        function may be registered per job attempt by calling this method repeatedly with
        different arguments. If the same function is registered twice with the same or different
        arguments, it will be called twice per job attempt.

        Examples for deferred functions are ones that handle cleanup of resources external to
        Toil, like Docker containers, files outside the work directory, etc.

        :param callable function: The function to be called after this job concludes.

        :param list args: The arguments to the function

        :param dict kwargs: The keyword arguments to the function
        """
        require( self.fileStore is not None, 'A deferred function may only be registered with a '
                                             'job while that job is running.')
        self.fileStore._registerDeferredFunction(DeferredFunction.create(function, *args, **kwargs))