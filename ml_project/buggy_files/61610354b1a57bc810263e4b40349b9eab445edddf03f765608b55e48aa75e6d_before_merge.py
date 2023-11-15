    def close(self, timeout=no_default):
        """ Close this client

        Clients will also close automatically when your Python session ends

        If you started a client without arguments like ``Client()`` then this
        will also close the local cluster that was started at the same time.

        See Also
        --------
        Client.restart
        """
        if timeout == no_default:
            timeout = self._timeout * 2
        # XXX handling of self.status here is not thread-safe
        if self.status == 'closed':
            return
        self.status = 'closing'

        if self.asynchronous:
            future = self._close()
            if timeout:
                future = gen.with_timeout(timedelta(seconds=timeout), future)
            return future

        if self._start_arg is None:
            with ignoring(AttributeError):
                self.cluster.close()

        sync(self.loop, self._close, fast=True)

        assert self.status == 'closed'

        if self._should_close_loop and not shutting_down():
            self._loop_runner.stop()

        with ignoring(AttributeError):
            dask.config.set(scheduler=self._previous_scheduler)
        with ignoring(AttributeError):
            dask.config.set(shuffle=self._previous_shuffle)
        if self.get == dask.config.get('get', None):
            del dask.config.config['get']