    def _wait_for_and_process_task(self, task):
        """Wait for a task to be ready and process the task.

        Args:
            task: The task to execute.
        """
        function_id = task.function_id()
        # Wait until the function to be executed has actually been registered
        # on this worker. We will push warnings to the user if we spend too
        # long in this loop.
        with log_span("ray:wait_for_function", worker=self):
            self._wait_for_function(function_id, task.driver_id().id())

        # Execute the task.
        # TODO(rkn): Consider acquiring this lock with a timeout and pushing a
        # warning to the user if we are waiting too long to acquire the lock
        # because that may indicate that the system is hanging, and it'd be
        # good to know where the system is hanging.
        log(event_type="ray:acquire_lock", kind=LOG_SPAN_START, worker=self)
        with self.lock:
            log(event_type="ray:acquire_lock", kind=LOG_SPAN_END,
                worker=self)

            function_name, _ = (self.functions[task.driver_id().id()]
                                [function_id.id()])
            contents = {"function_name": function_name,
                        "task_id": task.task_id().hex(),
                        "worker_id": binary_to_hex(self.worker_id)}
            with log_span("ray:task", contents=contents, worker=self):
                self._process_task(task)

        # Push all of the log events to the global state store.
        flush_log()

        # Increase the task execution counter.
        (self.num_task_executions[task.driver_id().id()]
                                 [function_id.id()]) += 1

        reached_max_executions = (
            self.num_task_executions[task.driver_id().id()]
                                    [function_id.id()] ==
            self.function_properties[task.driver_id().id()]
                                    [function_id.id()].max_calls)
        if reached_max_executions:
            ray.worker.global_worker.local_scheduler_client.disconnect()
            os._exit(0)