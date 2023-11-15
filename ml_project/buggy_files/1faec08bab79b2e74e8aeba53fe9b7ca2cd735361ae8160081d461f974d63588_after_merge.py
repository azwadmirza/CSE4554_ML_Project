    def __init__(self, root, db_dir=None):
        """Create a Database for Spack installations under ``root``.

        A Database is a cache of Specs data from ``$prefix/spec.yaml``
        files in Spack installation directories.

        By default, Database files (data and lock files) are stored
        under ``root/.spack-db``, which is created if it does not
        exist.  This is the ``db_dir``.

        The Database will attempt to read an ``index.yaml`` file in
        ``db_dir``.  If it does not find one, it will be created when
        needed by scanning the entire Database root for ``spec.yaml``
        files according to Spack's ``DirectoryLayout``.

        Caller may optionally provide a custom ``db_dir`` parameter
        where data will be stored.  This is intended to be used for
        testing the Database class.

        """
        self.root = root

        if db_dir is None:
            # If the db_dir is not provided, default to within the db root.
            self._db_dir = join_path(self.root, _db_dirname)
        else:
            # Allow customizing the database directory location for testing.
            self._db_dir = db_dir

        # Set up layout of database files within the db dir
        self._index_path = join_path(self._db_dir, 'index.yaml')
        self._lock_path = join_path(self._db_dir, 'lock')

        # This is for other classes to use to lock prefix directories.
        self.prefix_lock_path = join_path(self._db_dir, 'prefix_lock')

        # Create needed directories and files
        if not os.path.exists(self._db_dir):
            mkdirp(self._db_dir)

        # initialize rest of state.
        self.lock = Lock(self._lock_path)
        self._data = {}

        # whether there was an error at the start of a read transaction
        self._error = None