    def _run_mini_scheduler_on_child_tasks(self, session=None) -> None:
        if conf.getboolean('scheduler', 'schedule_after_task_execution', fallback=True):
            from airflow.models.dagrun import DagRun  # Avoid circular import

            try:
                # Re-select the row with a lock
                dag_run = with_row_locks(
                    session.query(DagRun).filter_by(
                        dag_id=self.dag_id,
                        execution_date=self.execution_date,
                    ),
                    session=session,
                ).one()

                # Get a partial dag with just the specific tasks we want to
                # examine. In order for dep checks to work correctly, we
                # include ourself (so TriggerRuleDep can check the state of the
                # task we just executed)
                partial_dag = self.task.dag.partial_subset(
                    self.task.downstream_task_ids,
                    include_downstream=False,
                    include_upstream=False,
                    include_direct_upstream=True,
                )

                dag_run.dag = partial_dag
                info = dag_run.task_instance_scheduling_decisions(session)

                skippable_task_ids = {
                    task_id
                    for task_id in partial_dag.task_ids
                    if task_id not in self.task.downstream_task_ids
                }

                schedulable_tis = [ti for ti in info.schedulable_tis if ti.task_id not in skippable_task_ids]
                for schedulable_ti in schedulable_tis:
                    if not hasattr(schedulable_ti, "task"):
                        schedulable_ti.task = self.task.dag.get_task(schedulable_ti.task_id)

                num = dag_run.schedule_tis(schedulable_tis)
                self.log.info("%d downstream tasks scheduled from follow-on schedule check", num)

                session.commit()
            except OperationalError as e:
                # Any kind of DB error here is _non fatal_ as this block is just an optimisation.
                self.log.info(
                    f"Skipping mini scheduling run due to exception: {e.statement}",
                    exc_info=True,
                )
                session.rollback()