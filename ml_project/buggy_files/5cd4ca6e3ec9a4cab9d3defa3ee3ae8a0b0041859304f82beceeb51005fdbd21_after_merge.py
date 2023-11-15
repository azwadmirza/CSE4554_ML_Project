    def _execute(self, query, args=None, fetchall=False, fetchone=False):
        """
        Executes DB query

        :param query: Query to execute
        :param args: Arguments in query
        :param fetchall: Boolean to indicate all results must be fetched
        :param fetchone: Boolean to indicate one result must be fetched (to walk results for instance)
        :return: query results
        """
        try:
            if not args:
                sql_results = self.connection.cursor().execute(query)
            else:
                sql_results = self.connection.cursor().execute(query, args)
            if fetchall:
                return sql_results.fetchall()
            elif fetchone:
                return sql_results.fetchone()
            else:
                return sql_results
        except sqlite3.OperationalError as e:
            # This errors user should be able to fix it.
            if 'unable to open database file' in e.args[0] or \
               'database is locked' in e.args[0] or \
               'database or disk is full' in e.args[0]:
                logger.log(u'DB error: {0!r}'.format(e), logger.WARNING)
            else:
                logger.log(u'DB error: {0!r}'.format(e), logger.ERROR)
                raise
        except Exception as e:
            logger.log(u'DB error: {0!r}'.format(e), logger.ERROR)
            raise