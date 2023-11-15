    def _create_dag_runs(self, dag_models: Iterable[DagModel], session: Session) -> None:
        """
        Unconditionally create a DAG run for the given DAG, and update the dag_model's fields to control
        if/when the next DAGRun should be created
        """
        # Bulk Fetch DagRuns with dag_id and execution_date same
        # as DagModel.dag_id and DagModel.next_dagrun
        # This list is used to verify if the DagRun already exist so that we don't attempt to create
        # duplicate dag runs
        active_dagruns = (
            session.query(DagRun.dag_id, DagRun.execution_date)
            .filter(
                tuple_(DagRun.dag_id, DagRun.execution_date).in_(
                    [(dm.dag_id, dm.next_dagrun) for dm in dag_models]
                )
            )
            .all()
        )

        for dag_model in dag_models:
            try:
                dag = self.dagbag.get_dag(dag_model.dag_id, session=session)
            except SerializedDagNotFound:
                self.log.exception("DAG '%s' not found in serialized_dag table", dag_model.dag_id)
                continue

            dag_hash = self.dagbag.dags_hash.get(dag.dag_id)
            # Explicitly check if the DagRun already exists. This is an edge case
            # where a Dag Run is created but `DagModel.next_dagrun` and `DagModel.next_dagrun_create_after`
            # are not updated.
            # We opted to check DagRun existence instead
            # of catching an Integrity error and rolling back the session i.e
            # we need to run self._update_dag_next_dagruns if the Dag Run already exists or if we
            # create a new one. This is so that in the next Scheduling loop we try to create new runs
            # instead of falling in a loop of Integrity Error.
            if (dag.dag_id, dag_model.next_dagrun) not in active_dagruns:
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