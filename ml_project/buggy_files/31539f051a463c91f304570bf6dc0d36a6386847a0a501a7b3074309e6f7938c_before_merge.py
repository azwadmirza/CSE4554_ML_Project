    def _create_dag_runs(self, dag_models: Iterable[DagModel], session: Session) -> None:
        """
        Unconditionally create a DAG run for the given DAG, and update the dag_model's fields to control
        if/when the next DAGRun should be created
        """
        for dag_model in dag_models:
            dag = self.dagbag.get_dag(dag_model.dag_id, session=session)
            dag_hash = self.dagbag.dags_hash.get(dag.dag_id)
            dag.create_dagrun(
                run_type=DagRunType.SCHEDULED,
                execution_date=dag_model.next_dagrun,
                start_date=timezone.utcnow(),
                state=State.RUNNING,
                external_trigger=False,
                session=session,
                dag_hash=dag_hash,
                creating_job_id=self.id,
            )

        self._update_dag_next_dagruns(dag_models, session)