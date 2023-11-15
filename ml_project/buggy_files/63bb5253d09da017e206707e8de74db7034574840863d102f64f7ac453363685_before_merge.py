    def sync_to_db(self, session: Optional[Session] = None):
        """Save attributes about list of DAG to the DB."""
        # To avoid circular import - airflow.models.dagbag -> airflow.models.dag -> airflow.models.dagbag
        from airflow.models.dag import DAG
        from airflow.models.serialized_dag import SerializedDagModel

        def _serialze_dag_capturing_errors(dag, session):
            """
            Try to serialize the dag to the DB, but make a note of any errors.

            We can't place them directly in import_errors, as this may be retried, and work the next time
            """
            if dag.is_subdag:
                return []
            try:
                # We cant use bulk_write_to_db as we want to capture each error individually
                SerializedDagModel.write_dag(
                    dag,
                    min_update_interval=settings.MIN_SERIALIZED_DAG_UPDATE_INTERVAL,
                    session=session,
                )
                return []
            except OperationalError:
                raise
            except Exception:  # pylint: disable=broad-except
                return [(dag.fileloc, traceback.format_exc(limit=-self.dagbag_import_error_traceback_depth))]

        # Retry 'DAG.bulk_write_to_db' & 'SerializedDagModel.bulk_sync_to_db' in case
        # of any Operational Errors
        # In case of failures, provide_session handles rollback
        for attempt in tenacity.Retrying(
            retry=tenacity.retry_if_exception_type(exception_types=OperationalError),
            wait=tenacity.wait_random_exponential(multiplier=0.5, max=5),
            stop=tenacity.stop_after_attempt(settings.MAX_DB_RETRIES),
            before_sleep=tenacity.before_sleep_log(self.log, logging.DEBUG),
            reraise=True,
        ):
            with attempt:
                serialize_errors = []
                self.log.debug(
                    "Running dagbag.sync_to_db with retries. Try %d of %d",
                    attempt.retry_state.attempt_number,
                    settings.MAX_DB_RETRIES,
                )
                self.log.debug("Calling the DAG.bulk_sync_to_db method")
                try:
                    # Write Serialized DAGs to DB, capturing errors
                    for dag in self.dags.values():
                        serialize_errors.extend(_serialze_dag_capturing_errors(dag, session))

                    DAG.bulk_write_to_db(self.dags.values(), session=session)
                except OperationalError:
                    session.rollback()
                    raise
                # Only now we are "complete" do we update import_errors - don't want to record errors from
                # previous failed attempts
                self.import_errors.update(dict(serialize_errors))