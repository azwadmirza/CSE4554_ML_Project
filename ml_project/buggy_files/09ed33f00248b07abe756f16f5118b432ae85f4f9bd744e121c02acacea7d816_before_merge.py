    def execute(self, operations):  # type: (Operation) -> int
        self._total_operations = len(operations)
        for job_type in self._executed:
            self._executed[job_type] = 0
            self._skipped[job_type] = 0

        if operations and (self._enabled or self._dry_run):
            self._display_summary(operations)

        # We group operations by priority
        groups = itertools.groupby(operations, key=lambda o: -o.priority)
        self._sections = OrderedDict()
        for _, group in groups:
            tasks = []
            for operation in group:
                if self._shutdown:
                    break

                tasks.append(self._executor.submit(self._execute_operation, operation))

            try:
                wait(tasks)
            except KeyboardInterrupt:
                self._shutdown = True

            if self._shutdown:
                # Cancelling further tasks from being executed
                [task.cancel() for task in tasks]
                self._executor.shutdown(wait=True)

                break

        return 1 if self._shutdown else 0