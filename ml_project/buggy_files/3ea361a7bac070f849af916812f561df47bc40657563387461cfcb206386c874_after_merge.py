    def _do_scheduling(self, session) -> int:
        """
        This function is where the main scheduling decisions take places. It:

        - Creates any necessary DAG runs by examining the next_dagrun_create_after column of DagModel

          Since creating Dag Runs is a relatively time consuming process, we select only 10 dags by default
          (configurable via ``scheduler.max_dagruns_to_create_per_loop`` setting) - putting this higher will
          mean one scheduler could spend a chunk of time creating dag runs, and not ever get around to
          scheduling tasks.

        - Finds the "next n oldest" running DAG Runs to examine for scheduling (n=20 by default, configurable
          via ``scheduler.max_dagruns_per_loop_to_schedule`` config setting) and tries to progress state (TIs
          to SCHEDULED, or DagRuns to SUCCESS/FAILURE etc)

          By "next oldest", we mean hasn't been examined/scheduled in the most time.

          The reason we don't select all dagruns at once because the rows are selected with row locks, meaning
          that only one scheduler can "process them", even it it is waiting behind other dags. Increasing this
          limit will allow more throughput for smaller DAGs but will likely slow down throughput for larger
          (>500 tasks.) DAGs

        - Then, via a Critical Section (locking the rows of the Pool model) we queue tasks, and then send them
          to the executor.

          See docs of _critical_section_execute_task_instances for more.

        :return: Number of TIs enqueued in this iteration
        :rtype: int
        """
        # Put a check in place to make sure we don't commit unexpectedly
        with prohibit_commit(session) as guard:

            if settings.USE_JOB_SCHEDULE:
                self._create_dagruns_for_dags(guard, session)

            dag_runs = self._get_next_dagruns_to_examine(session)
            # Bulk fetch the currently active dag runs for the dags we are
            # examining, rather than making one query per DagRun

            # TODO: This query is probably horribly inefficient (though there is an
            # index on (dag_id,state)). It is to deal with the case when a user
            # clears more than max_active_runs older tasks -- we don't want the
            # scheduler to suddenly go and start running tasks from all of the
            # runs. (AIRFLOW-137/GH #1442)
            #
            # The longer term fix would be to have `clear` do this, and put DagRuns
            # in to the queued state, then take DRs out of queued before creating
            # any new ones

            # Build up a set of execution_dates that are "active" for a given
            # dag_id -- only tasks from those runs will be scheduled.
            active_runs_by_dag_id = defaultdict(set)

            query = (
                session.query(
                    TI.dag_id,
                    TI.execution_date,
                )
                .filter(
                    TI.dag_id.in_(list({dag_run.dag_id for dag_run in dag_runs})),
                    TI.state.notin_(list(State.finished) + [State.REMOVED]),
                )
                .group_by(TI.dag_id, TI.execution_date)
            )

            for dag_id, execution_date in query:
                active_runs_by_dag_id[dag_id].add(execution_date)

            for dag_run in dag_runs:
                # Use try_except to not stop the Scheduler when a Serialized DAG is not found
                # This takes care of Dynamic DAGs especially
                # SerializedDagNotFound should not happen here in the same loop because the DagRun would
                # not be created in self._create_dag_runs if Serialized DAG does not exist
                # But this would take care of the scenario when the Scheduler is restarted after DagRun is
                # created and the DAG is deleted / renamed
                try:
                    self._schedule_dag_run(dag_run, active_runs_by_dag_id.get(dag_run.dag_id, set()), session)
                except SerializedDagNotFound:
                    self.log.exception("DAG '%s' not found in serialized_dag table", dag_run.dag_id)
                    continue

            guard.commit()

            # Without this, the session has an invalid view of the DB
            session.expunge_all()
            # END: schedule TIs

            try:
                if self.executor.slots_available <= 0:
                    # We know we can't do anything here, so don't even try!
                    self.log.debug("Executor full, skipping critical section")
                    return 0

                timer = Stats.timer('scheduler.critical_section_duration')
                timer.start()

                # Find anything TIs in state SCHEDULED, try to QUEUE it (send it to the executor)
                num_queued_tis = self._critical_section_execute_task_instances(session=session)

                # Make sure we only sent this metric if we obtained the lock, otherwise we'll skew the
                # metric, way down
                timer.stop(send=True)
            except OperationalError as e:
                timer.stop(send=False)

                if is_lock_not_available_error(error=e):
                    self.log.debug("Critical section lock held by another Scheduler")
                    Stats.incr('scheduler.critical_section_busy')
                    session.rollback()
                    return 0
                raise

            guard.commit()
            return num_queued_tis