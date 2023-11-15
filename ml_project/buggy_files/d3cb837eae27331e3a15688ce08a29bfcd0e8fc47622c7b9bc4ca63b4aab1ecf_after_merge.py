    def __init__(
        self,
        table_name,
        key_columns,
        fixed_length_key=True,
        credentials=None,
        url=None,
        connection_string=None,
        engine=None,
        store_name=None,
        suppress_store_backend_id=False,
        manually_initialize_store_backend_id: str = "",
        **kwargs,
    ):
        super().__init__(
            fixed_length_key=fixed_length_key,
            suppress_store_backend_id=suppress_store_backend_id,
            manually_initialize_store_backend_id=manually_initialize_store_backend_id,
            store_name=store_name,
        )
        if not sa:
            raise ge_exceptions.DataContextError(
                "ModuleNotFoundError: No module named 'sqlalchemy'"
            )

        if not self.fixed_length_key:
            raise ge_exceptions.InvalidConfigError(
                "DatabaseStoreBackend requires use of a fixed-length-key"
            )

        self._schema_name = None
        self._credentials = credentials
        self._connection_string = connection_string
        self._url = url

        if engine is not None:
            if credentials is not None:
                logger.warning(
                    "Both credentials and engine were provided during initialization of SqlAlchemyExecutionEngine. "
                    "Ignoring credentials."
                )
            self.engine = engine
        elif credentials is not None:
            self.engine = self._build_engine(credentials=credentials, **kwargs)
        elif connection_string is not None:
            self.engine = sa.create_engine(connection_string, **kwargs)
        elif url is not None:
            self.drivername = urlparse(url).scheme
            self.engine = sa.create_engine(url, **kwargs)
        else:
            raise ge_exceptions.InvalidConfigError(
                "Credentials, url, connection_string, or an engine are required for a DatabaseStoreBackend."
            )

        meta = MetaData(schema=self._schema_name)
        self.key_columns = key_columns
        # Dynamically construct a SQLAlchemy table with the name and column names we'll use
        cols = []
        for column in key_columns:
            if column == "value":
                raise ge_exceptions.InvalidConfigError(
                    "'value' cannot be used as a key_element name"
                )
            cols.append(Column(column, String, primary_key=True))
        cols.append(Column("value", String))
        try:
            table = Table(table_name, meta, autoload=True, autoload_with=self.engine)
            # We do a "light" check: if the columns' names match, we will proceed, otherwise, create the table
            if {str(col.name).lower() for col in table.columns} != (
                set(key_columns) | {"value"}
            ):
                raise ge_exceptions.StoreBackendError(
                    f"Unable to use table {table_name}: it exists, but does not have the expected schema."
                )
        except NoSuchTableError:
            table = Table(table_name, meta, *cols)
            try:
                if self._schema_name:
                    self.engine.execute(
                        f"CREATE SCHEMA IF NOT EXISTS {self._schema_name};"
                    )
                meta.create_all(self.engine)
            except SQLAlchemyError as e:
                raise ge_exceptions.StoreBackendError(
                    f"Unable to connect to table {table_name} because of an error. It is possible your table needs to be migrated to a new schema.  SqlAlchemyError: {str(e)}"
                )
        self._table = table
        # Initialize with store_backend_id
        self._store_backend_id = None
        self._store_backend_id = self.store_backend_id