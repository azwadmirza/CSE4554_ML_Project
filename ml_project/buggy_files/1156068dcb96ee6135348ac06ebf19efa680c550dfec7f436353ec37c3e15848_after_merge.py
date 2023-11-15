    def _get_connection(self, write=False):
        """Prepare the connection for action.

        Arguments:
            write (bool): are we a writer?
        """
        if self._session is not None:
            return
        self._lock.acquire()
        try:
            if self._session is not None:
                return
            self._cluster = cassandra.cluster.Cluster(
                self.servers, port=self.port,
                auth_provider=self.auth_provider,
                **self.cassandra_options)
            self._session = self._cluster.connect(self.keyspace)

            # We're forced to do concatenation below, as formatting would
            # blow up on superficial %s that'll be processed by Cassandra
            self._write_stmt = cassandra.query.SimpleStatement(
                Q_INSERT_RESULT.format(
                    table=self.table, expires=self.cqlexpires),
            )
            self._write_stmt.consistency_level = self.write_consistency

            self._read_stmt = cassandra.query.SimpleStatement(
                Q_SELECT_RESULT.format(table=self.table),
            )
            self._read_stmt.consistency_level = self.read_consistency

            if write:
                # Only possible writers "workers" are allowed to issue
                # CREATE TABLE.  This is to prevent conflicting situations
                # where both task-creator and task-executor would issue it
                # at the same time.

                # Anyway; if you're doing anything critical, you should
                # have created this table in advance, in which case
                # this query will be a no-op (AlreadyExists)
                make_stmt = cassandra.query.SimpleStatement(
                    Q_CREATE_RESULT_TABLE.format(table=self.table),
                )
                make_stmt.consistency_level = self.write_consistency

                try:
                    self._session.execute(make_stmt)
                except cassandra.AlreadyExists:
                    pass

        except cassandra.OperationTimedOut:
            # a heavily loaded or gone Cassandra cluster failed to respond.
            # leave this class in a consistent state
            if self._cluster is not None:
                self._cluster.shutdown()     # also shuts down _session

            self._cluster = None
            self._session = None
            raise   # we did fail after all - reraise
        finally:
            self._lock.release()