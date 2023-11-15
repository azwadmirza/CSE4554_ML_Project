    def _update_dag_next_dagruns(self, dag_models: Iterable[DagModel], session: Session) -> None:
        """
        Bulk update the next_dagrun and next_dagrun_create_after for all the dags.

        We batch the select queries to get info about all the dags at once
        """
        # Check max_active_runs, to see if we are _now_ at the limit for any of
        # these dag? (we've just created a DagRun for them after all)
        active_runs_of_dags = dict(
            session.query(DagRun.dag_id, func.count('*'))
            .filter(
                DagRun.dag_id.in_([o.dag_id for o in dag_models]),
                DagRun.state == State.RUNNING,  # pylint: disable=comparison-with-callable
                DagRun.external_trigger.is_(False),
            )
            .group_by(DagRun.dag_id)
            .all()
        )

        for dag_model in dag_models:
            dag = self.dagbag.get_dag(dag_model.dag_id, session=session)
            active_runs_of_dag = active_runs_of_dags.get(dag.dag_id, 0)
            if dag.max_active_runs and active_runs_of_dag >= dag.max_active_runs:
                self.log.info(
                    "DAG %s is at (or above) max_active_runs (%d of %d), not creating any more runs",
                    dag.dag_id,
                    active_runs_of_dag,
                    dag.max_active_runs,
                )
                dag_model.next_dagrun_create_after = None
            else:
                dag_model.next_dagrun, dag_model.next_dagrun_create_after = dag.next_dagrun_info(
                    dag_model.next_dagrun
                )