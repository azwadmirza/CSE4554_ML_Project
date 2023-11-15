    def _change_state_for_tis_without_dagrun(
        self, old_states: List[str], new_state: str, session: Session = None
    ) -> None:
        """
        For all DAG IDs in the DagBag, look for task instances in the
        old_states and set them to new_state if the corresponding DagRun
        does not exist or exists but is not in the running state. This
        normally should not happen, but it can if the state of DagRuns are
        changed manually.

        :param old_states: examine TaskInstances in this state
        :type old_states: list[airflow.utils.state.State]
        :param new_state: set TaskInstances to this state
        :type new_state: airflow.utils.state.State
        """
        tis_changed = 0
        query = (
            session.query(models.TaskInstance)
            .outerjoin(models.TaskInstance.dag_run)
            .filter(models.TaskInstance.dag_id.in_(list(self.dagbag.dag_ids)))
            .filter(models.TaskInstance.state.in_(old_states))
            .filter(
                or_(
                    # pylint: disable=comparison-with-callable
                    models.DagRun.state != State.RUNNING,
                    # pylint: disable=no-member
                    models.DagRun.state.is_(None),
                )
            )
        )
        # We need to do this for mysql as well because it can cause deadlocks
        # as discussed in https://issues.apache.org/jira/browse/AIRFLOW-2516
        if self.using_sqlite or self.using_mysql:
            tis_to_change: List[TI] = with_row_locks(
                query, of=TI, session=session, **skip_locked(session=session)
            ).all()
            for ti in tis_to_change:
                ti.set_state(new_state, session=session)
                tis_changed += 1
        else:
            subq = query.subquery()
            current_time = timezone.utcnow()
            ti_prop_update = {
                models.TaskInstance.state: new_state,
                models.TaskInstance.start_date: current_time,
            }

            # Only add end_date and duration if the new_state is 'success', 'failed' or 'skipped'
            if new_state in State.finished:
                ti_prop_update.update(
                    {
                        models.TaskInstance.end_date: current_time,
                        models.TaskInstance.duration: 0,
                    }
                )

            tis_changed = (
                session.query(models.TaskInstance)
                .filter(
                    models.TaskInstance.dag_id == subq.c.dag_id,
                    models.TaskInstance.task_id == subq.c.task_id,
                    models.TaskInstance.execution_date == subq.c.execution_date,
                )
                .update(ti_prop_update, synchronize_session=False)
            )

        if tis_changed > 0:
            session.flush()
            self.log.warning(
                "Set %s task instances to state=%s as their associated DagRun was not in RUNNING state",
                tis_changed,
                new_state,
            )
            Stats.gauge('scheduler.tasks.without_dagrun', tis_changed)