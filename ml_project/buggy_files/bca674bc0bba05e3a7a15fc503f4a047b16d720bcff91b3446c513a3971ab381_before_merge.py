    def _upgrade_22_to_23(self):
        """
        Migrates the database to the new version.
        """
        self.status_update_func(u"Upgrading database from v%s to v%s..." % (22, 23))

        self.db.execute(u"""
DROP TABLE IF EXISTS BarterCast;
DROP INDEX IF EXISTS bartercast_idx;

DROP INDEX IF EXISTS Torrent_swift_torrent_hash_idx;
""")

        try:
            next(self.db.execute(u"SELECT * From sqlite_master WHERE name == '_tmp_Torrent' and type == 'table';"))

        except StopIteration:
            # no _tmp_Torrent table, check if the current Torrent table is new
            lines = [(0, u'torrent_id', u'integer', 1, None, 1),
                     (1, u'infohash', u'text', 1, None, 0),
                     (2, u'name', u'text', 0, None, 0),
                     (3, u'torrent_file_name', u'text', 0, None, 0),
                     (4, u'length', u'integer', 0, None, 0),
                     (5, u'creation_date', u'integer', 0, None, 0),
                     (6, u'num_files', u'integer', 0, None, 0),
                     (7, u'thumbnail', u'integer', 0, None, 0),
                     (8, u'insert_time', u'numeric', 0, None, 0),
                     (9, u'secret', u'integer', 0, None, 0),
                     (10, u'relevance', u'numeric', 0, u'0', 0),
                     (11, u'source_id', u'integer', 0, None, 0),
                     (12, u'category_id', u'integer', 0, None, 0),
                     (13, u'status_id', u'integer', 0, u'0', 0),
                     (14, u'num_seeders', u'integer', 0, None, 0),
                     (15, u'num_leechers', u'integer', 0, None, 0),
                     (16, u'comment', u'text', 0, None, 0),
                     (17, u'dispersy_id', u'integer', 0, None, 0),
                     (18, u'last_tracker_check', u'integer', 0, u'0', 0),
                     (19, u'tracker_check_retries', u'integer', 0, u'0', 0),
                     (20, u'next_tracker_check', u'integer', 0, u'0', 0)
                     ]
            i = 0
            is_new = True
            for line in self.db.execute(u"PRAGMA table_info(Torrent);"):
                if line != lines[i]:
                    is_new = False
                    break
                i += 1

            if not is_new:
                # create the temporary table
                self.db.execute(u"""
CREATE TABLE IF NOT EXISTS _tmp_Torrent (
  torrent_id       integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  infohash		   text NOT NULL,
  name             text,
  torrent_file_name text,
  length           integer,
  creation_date    integer,
  num_files        integer,
  thumbnail        integer,
  insert_time      numeric,
  secret           integer,
  relevance        numeric DEFAULT 0,
  source_id        integer,
  category_id      integer,
  status_id        integer DEFAULT 0,
  num_seeders      integer,
  num_leechers     integer,
  comment          text,
  dispersy_id      integer,
  last_tracker_check    integer DEFAULT 0,
  tracker_check_retries integer DEFAULT 0,
  next_tracker_check    integer DEFAULT 0
);
""")

                # migrate Torrent table
                keys = (u"torrent_id", u"infohash", u"name", u"torrent_file_name", u"length", u"creation_date",
                        u"num_files", u"thumbnail", u"insert_time", u"secret", u"relevance", u"source_id",
                        u"category_id", u"status_id", u"num_seeders", u"num_leechers", u"comment", u"dispersy_id",
                        u"last_tracker_check", u"tracker_check_retries", u"next_tracker_check")

                keys_str = u", ".join(keys)
                values_str = u"?," * len(keys)
                insert_stmt = u"INSERT INTO _tmp_Torrent(%s) VALUES(%s)" % (keys_str, values_str[:-1])
                current_count = 0

                results = self.db.execute(u"SELECT %s FROM Torrent;" % keys_str)
                new_torrents = []
                for torrent in results:
                    torrent_id, infohash, name, torrent_file_name = torrent[:4]

                    filepath = os.path.join(self.torrent_collecting_dir, hexlify(str2bin(infohash)) + u".torrent")

                    # Check if we have the actual .torrent
                    torrent_file_name = None
                    if os.path.exists(filepath):
                        torrent_file_name = filepath
                        tdef = TorrentDef.load(filepath)
                        # Use the name on the .torrent file instead of the one stored in the database.
                        name = tdef.get_name_as_unicode() or name

                    new_torrents.append((torrent_id, infohash, name, torrent_file_name) + torrent[4:])

                    current_count += 1
                    self.status_update_func(u"Upgrading database, %s records upgraded..." % current_count)

                self.status_update_func(u"All torrent entries processed, inserting in database...")
                self.db.executemany(insert_stmt, new_torrents)
                self.status_update_func(u"All updated torrent entries inserted.")

                self.db.execute(u"""
DROP TABLE IF EXISTS Torrent;
ALTER TABLE _tmp_Torrent RENAME TO Torrent;
""")

        # cleanup metadata tables
        self.db.execute(u"""
DROP TABLE IF EXISTS MetadataMessage;
DROP TABLE IF EXISTS MetadataData;

CREATE TABLE IF NOT EXISTS MetadataMessage (
  message_id             INTEGER PRIMARY KEY AUTOINCREMENT,
  dispersy_id            INTEGER NOT NULL,
  this_global_time       INTEGER NOT NULL,
  this_mid               TEXT NOT NULL,
  infohash               TEXT NOT NULL,
  previous_mid           TEXT,
  previous_global_time   INTEGER
);

CREATE TABLE IF NOT EXISTS MetadataData (
  message_id  INTEGER,
  data_key    TEXT NOT NULL,
  data_value  INTEGER,
  FOREIGN KEY (message_id) REFERENCES MetadataMessage(message_id) ON DELETE CASCADE
);
""")

        # cleanup all SearchCommunity and MetadataCommunity data in dispersy database
        self._purge_old_search_metadata_communities()

        # update database version
        self.db.write_version(23)