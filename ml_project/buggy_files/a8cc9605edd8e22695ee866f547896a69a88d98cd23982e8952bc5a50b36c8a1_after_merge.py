    def __init__(self, config):
        # MySQL - mysql://username:password@localhost/db
        # SQLite - sqlite:////home/sopel/.sopel/default.db
        db_type = config.core.db_type

        # Handle SQLite explicitly as a default
        if db_type == 'sqlite':
            path = config.core.db_filename
            config_dir, config_file = os.path.split(config.filename)
            config_name, _ = os.path.splitext(config_file)
            if path is None:
                path = os.path.join(config_dir, config_name + '.db')
            path = os.path.expanduser(path)
            if not os.path.isabs(path):
                path = os.path.normpath(os.path.join(config_dir, path))
            self.filename = path
            self.url = 'sqlite:///%s' % path
        # Otherwise, handle all other database engines
        else:
            if db_type == 'mysql':
                drivername = config.core.db_driver or 'mysql'
            elif db_type == 'postgres':
                drivername = config.core.db_driver or 'postgresql'
            elif db_type == 'oracle':
                drivername = config.core.db_driver or 'oracle'
            elif db_type == 'mssql':
                drivername = config.core.db_driver or 'mssql+pymssql'
            elif db_type == 'firebird':
                drivername = config.core.db_driver or 'firebird+fdb'
            elif db_type == 'sybase':
                drivername = config.core.db_driver or 'sybase+pysybase'
            else:
                raise Exception('Unknown db_type')

            db_user = config.core.db_user
            db_pass = config.core.db_pass
            db_host = config.core.db_host
            db_port = config.core.db_port  # Optional
            db_name = config.core.db_name  # Optional, depending on DB

            # Ensure we have all our variables defined
            if db_user is None or db_pass is None or db_host is None:
                raise Exception('Please make sure the following core '
                                'configuration values are defined: '
                                'db_user, db_pass, db_host')
            self.url = URL(drivername=drivername, username=db_user, password=db_pass,
                           host=db_host, port=db_port, database=db_name)

        self.engine = create_engine(self.url)

        # Catch any errors connecting to database
        try:
            self.engine.connect()
        except OperationalError:
            print("OperationalError: Unable to connect to database.")
            raise

        # Create our tables
        BASE.metadata.create_all(self.engine)

        self.ssession = scoped_session(sessionmaker(bind=self.engine))