    def connect(self):
        self.logger.debug('Connecting to mongodb server.')
        try:
            self.client = pymongo.MongoClient(self.parameters.host,
                                              int(self.parameters.port))
        except pymongo.errors.ConnectionFailure:
            raise ValueError('Connection to mongodb server failed.')
        else:
            db = self.client[self.parameters.database]
            if hasattr(self.parameters, 'db_user') and hasattr(self.parameters, 'db_pass'):
                self.logger.debug('Trying to authenticate to database {}.'.format(self.parameters.database))
                try:
                    db.authenticate(name=self.parameters.db_user,
                                    password=self.parameters.db_pass)
                except pymongo.errors.OperationFailure:
                    raise ValueError('Authentication to database {} failed'.format(self.parameters.database))
            self.collection = db[self.parameters.collection]
            self.logger.info('Successfully connected to mongodb server.')