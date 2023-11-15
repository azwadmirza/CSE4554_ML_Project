    def get_dag(self, dag_id, session: Session = None):
        """
        Gets the DAG out of the dictionary, and refreshes it if expired

        :param dag_id: DAG Id
        :type dag_id: str
        """
        # Avoid circular import
        from airflow.models.dag import DagModel

        if self.read_dags_from_db:
            # Import here so that serialized dag is only imported when serialization is enabled
            from airflow.models.serialized_dag import SerializedDagModel

            if dag_id not in self.dags:
                # Load from DB if not (yet) in the bag
                self._add_dag_from_db(dag_id=dag_id, session=session)
                return self.dags.get(dag_id)

            # If DAG is in the DagBag, check the following
            # 1. if time has come to check if DAG is updated (controlled by min_serialized_dag_fetch_secs)
            # 2. check the last_updated column in SerializedDag table to see if Serialized DAG is updated
            # 3. if (2) is yes, fetch the Serialized DAG.
            min_serialized_dag_fetch_secs = timedelta(seconds=settings.MIN_SERIALIZED_DAG_FETCH_INTERVAL)
            if (
                dag_id in self.dags_last_fetched
                and timezone.utcnow() > self.dags_last_fetched[dag_id] + min_serialized_dag_fetch_secs
            ):
                sd_last_updated_datetime = SerializedDagModel.get_last_updated_datetime(
                    dag_id=dag_id,
                    session=session,
                )
                if sd_last_updated_datetime > self.dags_last_fetched[dag_id]:
                    self._add_dag_from_db(dag_id=dag_id, session=session)

            return self.dags.get(dag_id)

        # If asking for a known subdag, we want to refresh the parent
        dag = None
        root_dag_id = dag_id
        if dag_id in self.dags:
            dag = self.dags[dag_id]
            if dag.is_subdag:
                root_dag_id = dag.parent_dag.dag_id  # type: ignore

        # If DAG Model is absent, we can't check last_expired property. Is the DAG not yet synchronized?
        orm_dag = DagModel.get_current(root_dag_id, session=session)
        if not orm_dag:
            return self.dags.get(dag_id)

        # If the dag corresponding to root_dag_id is absent or expired
        is_missing = root_dag_id not in self.dags
        is_expired = orm_dag.last_expired and dag and dag.last_loaded < orm_dag.last_expired
        if is_missing or is_expired:
            # Reprocess source file
            found_dags = self.process_file(
                filepath=correct_maybe_zipped(orm_dag.fileloc), only_if_updated=False
            )

            # If the source file no longer exports `dag_id`, delete it from self.dags
            if found_dags and dag_id in [found_dag.dag_id for found_dag in found_dags]:
                return self.dags[dag_id]
            elif dag_id in self.dags:
                del self.dags[dag_id]
        return self.dags.get(dag_id)