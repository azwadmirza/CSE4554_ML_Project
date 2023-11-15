    def join_native(self, timeout=None, propagate=True,
                    interval=0.5, callback=None, no_ack=True,
                    on_message=None, on_interval=None,
                    disable_sync_subtasks=True):
        """Backend optimized version of :meth:`join`.

        .. versionadded:: 2.2

        Note that this does not support collecting the results
        for different task types using different backends.

        This is currently only supported by the amqp, Redis and cache
        result backends.
        """
        if disable_sync_subtasks:
            assert_will_not_block()
        order_index = None if callback else {
            result.id: i for i, result in enumerate(self.results)
        }
        acc = None if callback else [None for _ in range(len(self))]
        for task_id, meta in self.iter_native(timeout, interval, no_ack,
                                              on_message, on_interval):
            if isinstance(meta, list):
                value = []
                for children_result in meta:
                    value.append(children_result.get())
            else:
                value = meta['result']
                if propagate and meta['status'] in states.PROPAGATE_STATES:
                    raise value
            if callback:
                callback(task_id, value)
            else:
                acc[order_index[task_id]] = value
        return acc