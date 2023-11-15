    def update(
        self,
        jobs,
        file=None,
        visited=None,
        skip_until_dynamic=False,
        progress=False,
        create_inventory=False,
    ):
        """ Update the DAG by adding given jobs and their dependencies. """
        if visited is None:
            visited = set()
        producer = None
        exceptions = list()
        jobs = sorted(jobs, reverse=not self.ignore_ambiguity)
        cycles = list()

        for job in jobs:
            logger.dag_debug(dict(status="candidate", job=job))
            if file in job.input:
                cycles.append(job)
                continue
            if job in visited:
                cycles.append(job)
                continue
            try:
                self.check_periodic_wildcards(job)
                self.update_(
                    job,
                    visited=set(visited),
                    skip_until_dynamic=skip_until_dynamic,
                    progress=progress,
                    create_inventory=create_inventory,
                )
                # TODO this might fail if a rule discarded here is needed
                # elsewhere
                if producer:
                    if job < producer or self.ignore_ambiguity:
                        break
                    elif producer is not None:
                        raise AmbiguousRuleException(file, job, producer)
                producer = job
            except (
                MissingInputException,
                CyclicGraphException,
                PeriodicWildcardError,
                WorkflowError,
            ) as ex:
                exceptions.append(ex)
            except RecursionError as e:
                raise WorkflowError(
                    e,
                    "If building the DAG exceeds the recursion limit, "
                    "this is likely due to a cyclic dependency."
                    "E.g. you might have a sequence of rules that "
                    "can generate their own input. Try to make "
                    "the output files more specific. "
                    "A common pattern is to have different prefixes "
                    "in the output files of different rules."
                    + "\nProblematic file pattern: {}".format(file)
                    if file
                    else "",
                )
        if producer is None:
            if cycles:
                job = cycles[0]
                raise CyclicGraphException(job.rule, file, rule=job.rule)
            if len(exceptions) > 1:
                raise WorkflowError(*exceptions)
            elif len(exceptions) == 1:
                raise exceptions[0]
        else:
            logger.dag_debug(dict(status="selected", job=producer))
            logger.dag_debug(
                dict(
                    file=file,
                    msg="Producer found, hence exceptions are ignored.",
                    exception=WorkflowError(*exceptions),
                )
            )

        n = len(self.dependencies)
        if progress and n % 1000 == 0 and n and self._progress != n:
            logger.info("Processed {} potential jobs.".format(n))
            self._progress = n

        return producer