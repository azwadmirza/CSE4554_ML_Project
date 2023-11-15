    def _db_create(self, table, database):
        ''' A helper method to initialize the database and handles

        :param table: The table name to create
        :param database: The database uri to use
        '''
        self._engine = sqlalchemy.create_engine(database, echo=False)
        self._metadata = sqlalchemy.MetaData(self._engine)
        self._table = sqlalchemy.Table(table, self._metadata,
                                       sqlalchemy.Column('type', sqltypes.String(1)),
                                       sqlalchemy.Column('index', sqltypes.Integer),
                                       sqlalchemy.Column('value', sqltypes.Integer),
                                       UniqueConstraint('type', 'index', name='key'))
        self._table.create(checkfirst=True)
        self._connection = self._engine.connect()