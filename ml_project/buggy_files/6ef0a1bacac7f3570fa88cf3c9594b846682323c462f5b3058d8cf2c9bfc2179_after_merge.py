    def update_(
        self,
        job,
        visited=None,
        skip_until_dynamic=False,
        progress=False,
        create_inventory=False,
    ):
        """ Update the DAG by adding the given job and its dependencies. """
        if job in self.dependencies:
            return
        if visited is None:
            visited = set()
        visited.add(job)
        dependencies = self.dependencies[job]
        potential_dependencies = self.collect_potential_dependencies(job)

        skip_until_dynamic = skip_until_dynamic and not job.dynamic_output

        missing_input = set()
        producer = dict()
        exceptions = dict()
        for file, jobs in potential_dependencies.items():
            if create_inventory:
                # If possible, obtain inventory information starting from
                # given file and store it in the IOCache.
                # This should provide faster access to existence and mtime information
                # than querying file by file. If the file type does not support inventory
                # information, this call is a no-op.
                file.inventory()

            if not jobs:
                # no producing job found
                if not file.exists:
                    # file not found, hence missing input
                    missing_input.add(file)
                # file found, no problem
                continue

            try:
                selected_job = self.update(
                    jobs,
                    file=file,
                    visited=visited,
                    skip_until_dynamic=skip_until_dynamic or file in job.dynamic_input,
                    progress=progress,
                )
                producer[file] = selected_job
            except (
                MissingInputException,
                CyclicGraphException,
                PeriodicWildcardError,
                WorkflowError,
            ) as ex:
                if not file.exists:
                    self.delete_job(job, recursive=False)  # delete job from tree
                    raise ex
                else:
                    logger.dag_debug(
                        dict(
                            file=file,
                            msg="No producers found, but file is present on disk.",
                            exception=ex,
                        )
                    )

        for file, job_ in producer.items():
            dependencies[job_].add(file)
            self.depending[job_][job].add(file)

        if self.is_batch_rule(job.rule) and self.batch.is_final:
            # For the final batch, ensure that all input files from
            # previous batches are present on disk.
            if any(
                f for f in job.input if f not in potential_dependencies and not f.exists
            ):
                raise WorkflowError(
                    "Unable to execute batch {} because not all previous batches "
                    "have been completed before or files have been deleted.".format(
                        self.batch
                    )
                )

        if missing_input:
            self.delete_job(job, recursive=False)  # delete job from tree
            raise MissingInputException(job.rule, missing_input)

        if skip_until_dynamic:
            self._dynamic.add(job)