    def _handle_sql_errors(self):
        try:
            yield
        except sql.SqlKnownError as e:
            message.error("Failed to write history: {}".format(e.text()))