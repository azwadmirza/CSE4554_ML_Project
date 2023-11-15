    def reset(self):
        ''' Resets all the datastores to their default values '''
        self._metadata.drop_all()
        self._db_create(self.table, self.database)