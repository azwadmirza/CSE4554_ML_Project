    def next_dagruns_to_examine(
        cls,
        session: Session,
        max_number: Optional[int] = None,
    ):
        """
        Return the next DagRuns that the scheduler should attempt to schedule.

        This will return zero or more DagRun rows that are row-level-locked with a "SELECT ... FOR UPDATE"
        query, you should ensure that any scheduling decisions are made in a single transaction -- as soon as
        the transaction is committed it will be unlocked.

        :rtype: list[airflow.models.DagRun]
        """
        from airflow.models.dag import DagModel

        if max_number is None:
            max_number = cls.DEFAULT_DAGRUNS_TO_EXAMINE

        # TODO: Bake this query, it is run _A lot_
        query = (
            session.query(cls)
            .filter(cls.state == State.RUNNING, cls.run_type != DagRunType.BACKFILL_JOB)
            .join(
                DagModel,
                DagModel.dag_id == cls.dag_id,
            )
            .filter(
                DagModel.is_paused.is_(False),
                DagModel.is_active.is_(True),
            )
            .order_by(
                nulls_first(cls.last_scheduling_decision, session=session),
                cls.execution_date,
            )
        )

        if not settings.ALLOW_FUTURE_EXEC_DATES:
            query = query.filter(DagRun.execution_date <= func.now())

        return with_row_locks(
            query.limit(max_number), of=cls, session=session, **skip_locked(session=session)
        )