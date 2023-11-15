    def get(self, timeout=None, propagate=True, interval=0.5,
            no_ack=True, follow_parents=True, callback=None, on_message=None,
            on_interval=None, disable_sync_subtasks=True,
            EXCEPTION_STATES=states.EXCEPTION_STATES,
            PROPAGATE_STATES=states.PROPAGATE_STATES):
        """Wait until task is ready, and return its result.

        Warning:
           Waiting for tasks within a task may lead to deadlocks.
           Please read :ref:`task-synchronous-subtasks`.

        Warning:
           Backends use resources to store and transmit results. To ensure
           that resources are released, you must eventually call
           :meth:`~@AsyncResult.get` or :meth:`~@AsyncResult.forget` on
           EVERY :class:`~@AsyncResult` instance returned after calling
           a task.

        Arguments:
            timeout (float): How long to wait, in seconds, before the
                operation times out.
            propagate (bool): Re-raise exception if the task failed.
            interval (float): Time to wait (in seconds) before retrying to
                retrieve the result.  Note that this does not have any effect
                when using the RPC/redis result store backends, as they don't
                use polling.
            no_ack (bool): Enable amqp no ack (automatically acknowledge
                message).  If this is :const:`False` then the message will
                **not be acked**.
            follow_parents (bool): Re-raise any exception raised by
                parent tasks.
            disable_sync_subtasks (bool): Disable tasks to wait for sub tasks
                this is the default configuration. CAUTION do not enable this
                unless you must.

        Raises:
            celery.exceptions.TimeoutError: if `timeout` isn't
                :const:`None` and the result does not arrive within
                `timeout` seconds.
            Exception: If the remote call raised an exception then that
                exception will be re-raised in the caller process.
        """
        if self.ignored:
            return

        if disable_sync_subtasks:
            assert_will_not_block()
        _on_interval = promise()
        if follow_parents and propagate and self.parent:
            on_interval = promise(self._maybe_reraise_parent_error, weak=True)
            self._maybe_reraise_parent_error()
        if on_interval:
            _on_interval.then(on_interval)

        if self._cache:
            if propagate:
                self.maybe_throw(callback=callback)
            return self.result

        self.backend.add_pending_result(self)
        return self.backend.wait_for_pending(
            self, timeout=timeout,
            interval=interval,
            on_interval=_on_interval,
            no_ack=no_ack,
            propagate=propagate,
            callback=callback,
            on_message=on_message,
        )