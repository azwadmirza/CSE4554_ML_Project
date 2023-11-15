    def execute_delete_by_query(self, **kwargs):
        """ Executes an arbitrary delete_by_query."""
        with self._new_trace_span(operation="delete_by", **kwargs):
            results = self._execute_raw_query(
                self.es.delete_by_query, doc_type="_doc", **kwargs
            )
            return results