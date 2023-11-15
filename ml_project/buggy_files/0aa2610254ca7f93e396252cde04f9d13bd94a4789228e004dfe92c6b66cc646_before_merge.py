    def _execute(self, session=None):
        """
        Initializes all components required to run a dag for a specified date range and
        calls helper method to execute the tasks.
        """
        ti_status = BackfillJob._DagRunTaskStatus()

        start_date = self.bf_start_date

        # Get intervals between the start/end dates, which will turn into dag runs
        run_dates = self.dag.get_run_dates(start_date=start_date, end_date=self.bf_end_date)
        if self.run_backwards:
            tasks_that_depend_on_past = [t.task_id for t in self.dag.task_dict.values() if t.depends_on_past]
            if tasks_that_depend_on_past:
                raise AirflowException(
                    'You cannot backfill backwards because one or more tasks depend_on_past: {}'.format(
                        ",".join(tasks_that_depend_on_past)
                    )
                )
            run_dates = run_dates[::-1]

        if len(run_dates) == 0:
            self.log.info("No run dates were found for the given dates and dag interval.")
            return

        # picklin'
        pickle_id = None

        if not self.donot_pickle and self.executor_class not in (
            executor_constants.LOCAL_EXECUTOR,
            executor_constants.SEQUENTIAL_EXECUTOR,
            executor_constants.DASK_EXECUTOR,
        ):
            pickle = DagPickle(self.dag)
            session.add(pickle)
            session.commit()
            pickle_id = pickle.id

        executor = self.executor
        executor.start()

        ti_status.total_runs = len(run_dates)  # total dag runs in backfill

        try:  # pylint: disable=too-many-nested-blocks
            remaining_dates = ti_status.total_runs
            while remaining_dates > 0:
                dates_to_process = [
                    run_date for run_date in run_dates if run_date not in ti_status.executed_dag_run_dates
                ]

                self._execute_for_run_dates(
                    run_dates=dates_to_process,
                    ti_status=ti_status,
                    executor=executor,
                    pickle_id=pickle_id,
                    start_date=start_date,
                    session=session,
                )

                remaining_dates = ti_status.total_runs - len(ti_status.executed_dag_run_dates)
                err = self._collect_errors(ti_status=ti_status, session=session)
                if err:
                    raise BackfillUnfinished(err, ti_status)

                if remaining_dates > 0:
                    self.log.info(
                        "max_active_runs limit for dag %s has been reached "
                        " - waiting for other dag runs to finish",
                        self.dag_id,
                    )
                    time.sleep(self.delay_on_limit_secs)
        except (KeyboardInterrupt, SystemExit):
            self.log.warning("Backfill terminated by user.")

            # TODO: we will need to terminate running task instances and set the
            # state to failed.
            self._set_unfinished_dag_runs_to_failed(ti_status.active_runs)
        finally:
            session.commit()
            executor.end()

        self.log.info("Backfill done. Exiting.")