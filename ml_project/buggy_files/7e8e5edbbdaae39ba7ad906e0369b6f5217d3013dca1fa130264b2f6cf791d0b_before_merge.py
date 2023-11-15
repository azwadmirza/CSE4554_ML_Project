    def _new_transaction(self, conn, desc, after_callbacks, exception_callbacks,
                         func, *args, **kwargs):
        start = time.time()
        txn_id = self._TXN_ID

        # We don't really need these to be unique, so lets stop it from
        # growing really large.
        self._TXN_ID = (self._TXN_ID + 1) % (MAX_TXN_ID)

        name = "%s-%x" % (desc, txn_id, )

        transaction_logger.debug("[TXN START] {%s}", name)

        try:
            i = 0
            N = 5
            while True:
                try:
                    txn = conn.cursor()
                    txn = LoggingTransaction(
                        txn, name, self.database_engine, after_callbacks,
                        exception_callbacks,
                    )
                    r = func(txn, *args, **kwargs)
                    conn.commit()
                    return r
                except self.database_engine.module.OperationalError as e:
                    # This can happen if the database disappears mid
                    # transaction.
                    logger.warn(
                        "[TXN OPERROR] {%s} %s %d/%d",
                        name, e, i, N
                    )
                    if i < N:
                        i += 1
                        try:
                            conn.rollback()
                        except self.database_engine.module.Error as e1:
                            logger.warn(
                                "[TXN EROLL] {%s} %s",
                                name, e1,
                            )
                        continue
                    raise
                except self.database_engine.module.DatabaseError as e:
                    if self.database_engine.is_deadlock(e):
                        logger.warn("[TXN DEADLOCK] {%s} %d/%d", name, i, N)
                        if i < N:
                            i += 1
                            try:
                                conn.rollback()
                            except self.database_engine.module.Error as e1:
                                logger.warn(
                                    "[TXN EROLL] {%s} %s",
                                    name, e1,
                                )
                            continue
                    raise
        except Exception as e:
            logger.debug("[TXN FAIL] {%s} %s", name, e)
            raise
        finally:
            end = time.time()
            duration = end - start

            LoggingContext.current_context().add_database_transaction(duration)

            transaction_logger.debug("[TXN END] {%s} %f sec", name, duration)

            self._current_txn_total_time += duration
            self._txn_perf_counters.update(desc, start, end)
            sql_txn_timer.labels(desc).observe(duration)