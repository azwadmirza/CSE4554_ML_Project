    def bulk_write_to_db(cls, dags: Collection["DAG"], session=None):
        """
        Ensure the DagModel rows for the given dags are up-to-date in the dag table in the DB, including
        calculated fields.

        Note that this method can be called for both DAGs and SubDAGs. A SubDag is actually a SubDagOperator.

        :param dags: the DAG objects to save to the DB
        :type dags: List[airflow.models.dag.DAG]
        :return: None
        """
        if not dags:
            return

        log.info("Sync %s DAGs", len(dags))
        dag_by_ids = {dag.dag_id: dag for dag in dags}
        dag_ids = set(dag_by_ids.keys())
        query = (
            session.query(DagModel)
            .options(joinedload(DagModel.tags, innerjoin=False))
            .filter(DagModel.dag_id.in_(dag_ids))
        )
        orm_dags = with_row_locks(query, of=DagModel).all()

        existing_dag_ids = {orm_dag.dag_id for orm_dag in orm_dags}
        missing_dag_ids = dag_ids.difference(existing_dag_ids)

        for missing_dag_id in missing_dag_ids:
            orm_dag = DagModel(dag_id=missing_dag_id)
            dag = dag_by_ids[missing_dag_id]
            if dag.is_paused_upon_creation is not None:
                orm_dag.is_paused = dag.is_paused_upon_creation
            orm_dag.tags = []
            log.info("Creating ORM DAG for %s", dag.dag_id)
            session.add(orm_dag)
            orm_dags.append(orm_dag)

        # Get the latest dag run for each existing dag as a single query (avoid n+1 query)
        most_recent_dag_runs = dict(
            session.query(DagRun.dag_id, func.max_(DagRun.execution_date))
            .filter(
                DagRun.dag_id.in_(existing_dag_ids),
                or_(
                    DagRun.run_type == DagRunType.BACKFILL_JOB,
                    DagRun.run_type == DagRunType.SCHEDULED,
                ),
            )
            .group_by(DagRun.dag_id)
            .all()
        )

        # Get number of active dagruns for all dags we are processing as a single query.
        num_active_runs = dict(
            session.query(DagRun.dag_id, func.count('*'))
            .filter(
                DagRun.dag_id.in_(existing_dag_ids),
                DagRun.state == State.RUNNING,  # pylint: disable=comparison-with-callable
                DagRun.external_trigger.is_(False),
            )
            .group_by(DagRun.dag_id)
            .all()
        )

        for orm_dag in sorted(orm_dags, key=lambda d: d.dag_id):
            dag = dag_by_ids[orm_dag.dag_id]
            if dag.is_subdag:
                orm_dag.is_subdag = True
                orm_dag.fileloc = dag.parent_dag.fileloc  # type: ignore
                orm_dag.root_dag_id = dag.parent_dag.dag_id  # type: ignore
                orm_dag.owners = dag.parent_dag.owner  # type: ignore
            else:
                orm_dag.is_subdag = False
                orm_dag.fileloc = dag.fileloc
                orm_dag.owners = dag.owner
            orm_dag.is_active = True
            orm_dag.default_view = dag.default_view
            orm_dag.description = dag.description
            orm_dag.schedule_interval = dag.schedule_interval
            orm_dag.concurrency = dag.concurrency
            orm_dag.has_task_concurrency_limits = any(t.task_concurrency is not None for t in dag.tasks)

            orm_dag.calculate_dagrun_date_fields(
                dag,
                most_recent_dag_runs.get(dag.dag_id),
                num_active_runs.get(dag.dag_id, 0),
            )

            for orm_tag in list(orm_dag.tags):
                if orm_tag.name not in orm_dag.tags:
                    session.delete(orm_tag)
                orm_dag.tags.remove(orm_tag)
            if dag.tags:
                orm_tag_names = [t.name for t in orm_dag.tags]
                for dag_tag in list(dag.tags):
                    if dag_tag not in orm_tag_names:
                        dag_tag_orm = DagTag(name=dag_tag, dag_id=dag.dag_id)
                        orm_dag.tags.append(dag_tag_orm)
                        session.add(dag_tag_orm)

        if settings.STORE_DAG_CODE:
            DagCode.bulk_sync_to_db([dag.fileloc for dag in orm_dags])

        # Issue SQL/finish "Unit of Work", but let @provide_session commit (or if passed a session, let caller
        # decide when to commit
        session.flush()

        for dag in dags:
            cls.bulk_write_to_db(dag.subdags, session=session)