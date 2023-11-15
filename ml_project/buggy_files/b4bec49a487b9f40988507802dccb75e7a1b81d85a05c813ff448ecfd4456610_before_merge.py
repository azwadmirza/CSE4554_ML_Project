    def adopt_or_reset_orphaned_tasks(self, session: Session = None):
        """
        Reset any TaskInstance still in QUEUED or SCHEDULED states that were
        enqueued by a SchedulerJob that is no longer running.

        :return: the number of TIs reset
        :rtype: int
        """
        self.log.info("Resetting orphaned tasks for active dag runs")
        timeout = conf.getint('scheduler', 'scheduler_health_check_threshold')

        num_failed = (
            session.query(SchedulerJob)
            .filter(
                SchedulerJob.state == State.RUNNING,
                SchedulerJob.latest_heartbeat < (timezone.utcnow() - timedelta(seconds=timeout)),
            )
            .update({"state": State.FAILED})
        )

        if num_failed:
            self.log.info("Marked %d SchedulerJob instances as failed", num_failed)
            Stats.incr(self.__class__.__name__.lower() + '_end', num_failed)

        resettable_states = [State.SCHEDULED, State.QUEUED, State.RUNNING]
        query = (
            session.query(TI)
            .filter(TI.state.in_(resettable_states))
            # outerjoin is because we didn't use to have queued_by_job
            # set, so we need to pick up anything pre upgrade. This (and the
            # "or queued_by_job_id IS NONE") can go as soon as scheduler HA is
            # released.
            .outerjoin(TI.queued_by_job)
            .filter(or_(TI.queued_by_job_id.is_(None), SchedulerJob.state != State.RUNNING))
            .join(TI.dag_run)
            .filter(
                DagRun.run_type != DagRunType.BACKFILL_JOB,
                # pylint: disable=comparison-with-callable
                DagRun.state == State.RUNNING,
            )
            .options(load_only(TI.dag_id, TI.task_id, TI.execution_date))
        )

        # Lock these rows, so that another scheduler can't try and adopt these too
        tis_to_reset_or_adopt = with_row_locks(query, of=TI, **skip_locked(session=session)).all()
        to_reset = self.executor.try_adopt_task_instances(tis_to_reset_or_adopt)

        reset_tis_message = []
        for ti in to_reset:
            reset_tis_message.append(repr(ti))
            ti.state = State.NONE
            ti.queued_by_job_id = None

        for ti in set(tis_to_reset_or_adopt) - set(to_reset):
            ti.queued_by_job_id = self.id

        Stats.incr('scheduler.orphaned_tasks.cleared', len(to_reset))
        Stats.incr('scheduler.orphaned_tasks.adopted', len(tis_to_reset_or_adopt) - len(to_reset))

        if to_reset:
            task_instance_str = '\n\t'.join(reset_tis_message)
            self.log.info(
                "Reset the following %s orphaned TaskInstances:\n\t%s", len(to_reset), task_instance_str
            )

        # Issue SQL/finish "Unit of Work", but let @provide_session commit (or if passed a session, let caller
        # decide when to commit
        session.flush()
        return len(to_reset)