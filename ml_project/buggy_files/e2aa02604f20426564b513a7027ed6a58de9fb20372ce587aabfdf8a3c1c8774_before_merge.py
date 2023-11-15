    def slots_stats(
        *,
        lock_rows: bool = False,
        session: Session = None,
    ) -> Dict[str, PoolStats]:
        """
        Get Pool stats (Number of Running, Queued, Open & Total tasks)

        If ``lock_rows`` is True, and the database engine in use supports the ``NOWAIT`` syntax, then a
        non-blocking lock will be attempted -- if the lock is not available then SQLAlchemy will throw an
        OperationalError.

        :param lock_rows: Should we attempt to obtain a row-level lock on all the Pool rows returns
        :param session: SQLAlchemy ORM Session
        """
        from airflow.models.taskinstance import TaskInstance  # Avoid circular import

        pools: Dict[str, PoolStats] = {}

        query = session.query(Pool.pool, Pool.slots)

        if lock_rows:
            query = with_row_locks(query, **nowait(session))

        pool_rows: Iterable[Tuple[str, int]] = query.all()
        for (pool_name, total_slots) in pool_rows:
            pools[pool_name] = PoolStats(total=total_slots, running=0, queued=0, open=0)

        state_count_by_pool = (
            session.query(TaskInstance.pool, TaskInstance.state, func.count())
            .filter(TaskInstance.state.in_(list(EXECUTION_STATES)))
            .group_by(TaskInstance.pool, TaskInstance.state)
        ).all()

        # calculate queued and running metrics
        count: int
        for (pool_name, state, count) in state_count_by_pool:
            stats_dict: Optional[PoolStats] = pools.get(pool_name)
            if not stats_dict:
                continue
            # TypedDict key must be a string literal, so we use if-statements to set value
            if state == "running":
                stats_dict["running"] = count
            elif state == "queued":
                stats_dict["queued"] = count
            else:
                raise AirflowException(f"Unexpected state. Expected values: {EXECUTION_STATES}.")

        # calculate open metric
        for pool_name, stats_dict in pools.items():
            if stats_dict["total"] == -1:
                # -1 means infinite
                stats_dict["open"] = -1
            else:
                stats_dict["open"] = stats_dict["total"] - stats_dict["running"] - stats_dict["queued"]

        return pools