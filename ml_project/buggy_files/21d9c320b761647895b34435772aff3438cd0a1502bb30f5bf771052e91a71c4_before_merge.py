    def __init__(self, conf):

        db_path = conf.sqlite.path
        if db_path is None:
            db_path = xdg.BaseDirectory.save_data_path('khal') + '/khal.db'
        self.db_path = path.expanduser(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.debug = conf.debug
        self._create_default_tables()
        self._check_table_version()
        self.conf = conf