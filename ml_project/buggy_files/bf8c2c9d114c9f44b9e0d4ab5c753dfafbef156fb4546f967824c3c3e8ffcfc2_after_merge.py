    def _jobStoreExists(self):
        """
        Checks if job store exists by querying the existence of the statsFileIDs table. Note that
        this is the last component that is deleted in :meth:`.destroy`.
        """
        for attempt in retry_azure():
            with attempt:
                try:
                    table = self.tableService.query_tables(table_name=self._qualify('statsFileIDs'))
                except AzureMissingResourceHttpError as e:
                    if e.status_code == 404:
                        return False
                    else:
                        raise
                else:
                    return table is not None