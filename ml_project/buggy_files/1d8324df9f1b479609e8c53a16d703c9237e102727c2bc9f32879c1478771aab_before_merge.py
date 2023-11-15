    def _reproduce(
        self, executors: dict, jobs: Optional[int] = 1
    ) -> Mapping[str, Mapping[str, str]]:
        """Run dvc repro for the specified BaseExecutors in parallel.

        Returns:
            dict mapping stash revs to the successfully executed experiments
            for each stash rev.
        """
        result: Dict[str, Dict[str, str]] = defaultdict(dict)

        manager = Manager()
        pid_q = manager.Queue()
        with ProcessPoolExecutor(max_workers=jobs) as workers:
            futures = {}
            for rev, executor in executors.items():
                future = workers.submit(
                    executor.reproduce,
                    executor.dvc_dir,
                    pid_q,
                    rev,
                    name=executor.name,
                )
                futures[future] = (rev, executor)

            try:
                wait(futures)
            except KeyboardInterrupt:
                # forward SIGINT to any running executor processes and
                # cancel any remaining futures
                pids = {}
                while not pid_q.empty():
                    rev, pid = pid_q.get()
                    pids[rev] = pid
                for future, (rev, _) in futures.items():
                    if future.running():
                        os.kill(pids[rev], signal.SIGINT)
                    elif not future.done():
                        future.cancel()

            for future, (rev, executor) in futures.items():
                rev, executor = futures[future]
                exc = future.exception()

                try:
                    if exc is None:
                        exp_hash, force = future.result()
                        result[rev].update(
                            self._collect_executor(executor, exp_hash, force)
                        )
                    else:
                        # Checkpoint errors have already been logged
                        if not isinstance(exc, CheckpointKilledError):
                            logger.exception(
                                "Failed to reproduce experiment '%s'",
                                rev[:7],
                                exc_info=exc,
                            )
                except CancelledError:
                    logger.error(
                        "Cancelled before attempting to reproduce experiment "
                        "'%s'",
                        rev[:7],
                    )
                finally:
                    executor.cleanup()

        return result