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
            serial_operations = []
            for operation in group:
                if self._shutdown:
                    break

                # Some operations are unsafe, we mus execute them serially in a group
                # https://github.com/python-poetry/poetry/issues/3086
                # https://github.com/python-poetry/poetry/issues/2658
                #
                # We need to explicitly check source type here, see:
                # https://github.com/python-poetry/poetry-core/pull/98
                is_parallel_unsafe = operation.job_type == "uninstall" or (
                    operation.package.develop
                    and operation.package.source_type in {"directory", "git"}
                )
                if not operation.skipped and is_parallel_unsafe:
                    serial_operations.append(operation)
                    continue

                tasks.append(self._executor.submit(self._execute_operation, operation))

            try:
                wait(tasks)

                for operation in serial_operations:
                    wait([self._executor.submit(self._execute_operation, operation)])

            except KeyboardInterrupt:
                self._shutdown = True

            if self._shutdown:
                # Cancelling further tasks from being executed
                [task.cancel() for task in tasks]
                self._executor.shutdown(wait=True)

                break

        return 1 if self._shutdown else 0