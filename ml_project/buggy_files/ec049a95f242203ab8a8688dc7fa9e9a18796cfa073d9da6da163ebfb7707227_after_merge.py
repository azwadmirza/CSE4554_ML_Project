    def dags_needing_dagruns(cls, session: Session):
        """
        Return (and lock) a list of Dag objects that are due to create a new DagRun.

        This will return a resultset of rows  that is row-level-locked with a "SELECT ... FOR UPDATE" query,
        you should ensure that any scheduling decisions are made in a single transaction -- as soon as the
        transaction is committed it will be unlocked.
        """
        # TODO[HA]: Bake this query, it is run _A lot_
        # We limit so that _one_ scheduler doesn't try to do all the creation
        # of dag runs
        query = (
            session.query(cls)
            .filter(
                cls.is_paused.is_(False),
                cls.is_active.is_(True),
                cls.next_dagrun_create_after <= func.now(),
            )
            .order_by(cls.next_dagrun_create_after)
            .limit(cls.NUM_DAGS_PER_DAGRUN_QUERY)
        )

        return with_row_locks(query, of=cls, session=session, **skip_locked(session=session))