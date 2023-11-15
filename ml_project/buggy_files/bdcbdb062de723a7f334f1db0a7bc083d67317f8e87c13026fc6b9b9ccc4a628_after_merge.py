    def _setupdb(self, check_same_thread):
        """ Creates a backup database for the historian if doesn't exist."""

        _log.debug("Setting up backup DB.")
        self._connection = sqlite3.connect(
            'backup.sqlite',
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            check_same_thread=check_same_thread)

        c = self._connection.cursor()

        if self._backup_storage_limit_gb is not None:
            c.execute('''PRAGMA page_size''')
            page_size = c.fetchone()[0]
            max_storage_bytes = self._backup_storage_limit_gb * 1024 ** 3
            self.max_pages = max_storage_bytes / page_size

        c.execute("SELECT name FROM sqlite_master WHERE type='table' "
                  "AND name='outstanding';")

        if c.fetchone() is None:
            _log.debug("Configuring backup DB for the first time.")
            self._connection.execute('''PRAGMA auto_vacuum = FULL''')
            self._connection.execute('''CREATE TABLE outstanding
                                        (id INTEGER PRIMARY KEY,
                                         ts timestamp NOT NULL,
                                         source TEXT NOT NULL,
                                         topic_id INTEGER NOT NULL,
                                         value_string TEXT NOT NULL,
                                         header_string TEXT)''')
        else:
            #Check to see if we have a header_string column.
            c.execute("pragma table_info(outstanding);")
            name_index = 0
            for description in c.description:
                if description[0] == "name":
                    break
                name_index += 1

            found_header_column = False
            for row in c:
                if row[name_index] == "header_string":
                    found_header_column = True
                    break

            if not found_header_column:
                _log.info("Updating cache database to support storing header data.")
                c.execute("ALTER TABLE outstanding ADD COLUMN header_string text;")

        c.execute('''CREATE INDEX IF NOT EXISTS outstanding_ts_index
                                           ON outstanding (ts)''')

        c.execute("SELECT name FROM sqlite_master WHERE type='table' "
                  "AND name='metadata';")

        if c.fetchone() is None:
            self._connection.execute('''CREATE TABLE metadata
                                        (source TEXT NOT NULL,
                                         topic_id INTEGER NOT NULL,
                                         name TEXT NOT NULL,
                                         value TEXT NOT NULL,
                                         UNIQUE(topic_id, source, name))''')
        else:
            c.execute("SELECT * FROM metadata")
            for row in c:
                self._meta_data[(row[0], row[1])][row[2]] = row[3]

        c.execute("SELECT name FROM sqlite_master WHERE type='table' "
                  "AND name='topics';")

        if c.fetchone() is None:
            self._connection.execute('''create table topics
                                        (topic_id INTEGER PRIMARY KEY,
                                         topic_name TEXT NOT NULL,
                                         UNIQUE(topic_name))''')
        else:
            c.execute("SELECT * FROM topics")
            for row in c:
                self._backup_cache[row[0]] = row[1]
                self._backup_cache[row[1]] = row[0]

        c.close()

        self._connection.commit()