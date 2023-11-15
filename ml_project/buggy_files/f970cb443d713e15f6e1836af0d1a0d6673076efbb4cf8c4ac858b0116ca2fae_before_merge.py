    def _change_state_for_tasks_failed_to_execute(self, session: Session = None):
        """
        If there are tasks left over in the executor,
        we set them back to SCHEDULED to avoid creating hanging tasks.

        :param session: session for ORM operations
        """
        if not self.executor.queued_tasks:
            return

        filter_for_ti_state_change = [
            and_(
                TI.dag_id == dag_id,
                TI.task_id == task_id,
                TI.execution_date == execution_date,
                # The TI.try_number will return raw try_number+1 since the
                # ti is not running. And we need to -1 to match the DB record.
                TI._try_number == try_number - 1,  # pylint: disable=protected-access
                TI.state == State.QUEUED,
            )
            for dag_id, task_id, execution_date, try_number in self.executor.queued_tasks.keys()
        ]
        ti_query = session.query(TI).filter(or_(*filter_for_ti_state_change))
        tis_to_set_to_scheduled: List[TI] = with_row_locks(ti_query).all()
        if not tis_to_set_to_scheduled:
            return

        # set TIs to queued state
        filter_for_tis = TI.filter_for_tis(tis_to_set_to_scheduled)
        session.query(TI).filter(filter_for_tis).update(
            {TI.state: State.SCHEDULED, TI.queued_dttm: None}, synchronize_session=False
        )

        for task_instance in tis_to_set_to_scheduled:
            self.executor.queued_tasks.pop(task_instance.key)

        task_instance_str = "\n\t".join(repr(x) for x in tis_to_set_to_scheduled)
        self.log.info("Set the following tasks to scheduled state:\n\t%s", task_instance_str)