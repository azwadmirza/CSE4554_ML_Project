    def _upgrade_25_to_26(self):
        self.status_update_func(u"Upgrading database from v%s to v%s..." % (25, 26))

        # remove UserEventLog, TorrentSource, and TorrentCollecting tables
        self.status_update_func(u"Removing unused tables...")
        self.db.execute(u"""
DROP TABLE IF EXISTS UserEventLog;
DROP TABLE IF EXISTS TorrentSource;
DROP TABLE IF EXISTS TorrentCollecting;
""")

        # remove click_position, reranking_strategy, and progress from MyPreference
        self.status_update_func(u"Updating MyPreference table...")
        self.db.execute(u"""
CREATE TABLE _tmp_MyPreference (
  torrent_id     integer PRIMARY KEY NOT NULL,
  destination_path text NOT NULL,
  creation_time  integer NOT NULL
);

INSERT INTO _tmp_MyPreference SELECT torrent_id, destination_path, creation_time FROM MyPreference;

DROP TABLE MyPreference;
ALTER TABLE _tmp_MyPreference RENAME TO MyPreference;
""")

        # remove source_id and thumbnail columns from Torrent table
        # replace torrent_file_name column with is_collected column
        # change CollectedTorrent view
        self.status_update_func(u"Updating Torrent table...")
        self.db.execute(u"""
CREATE TABLE _tmp_Torrent (
  torrent_id       integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  infohash		   text NOT NULL,
  name             text,
  length           integer,
  creation_date    integer,
  num_files        integer,
  insert_time      numeric,
  secret           integer,
  relevance        numeric DEFAULT 0,
  category_id      integer,
  status_id        integer DEFAULT 0,
  num_seeders      integer,
  num_leechers     integer,
  comment          text,
  dispersy_id      integer,
  is_collected     integer DEFAULT 0,
  last_tracker_check    integer DEFAULT 0,
  tracker_check_retries integer DEFAULT 0,
  next_tracker_check    integer DEFAULT 0
);

UPDATE Torrent SET torrent_file_name = '1' WHERE torrent_file_name IS NOT NULL;
UPDATE Torrent SET torrent_file_name = '0' WHERE torrent_file_name IS NULL;

INSERT INTO _tmp_Torrent
SELECT torrent_id, infohash, name, length, creation_date, num_files, insert_time, secret, relevance, category_id,
status_id, num_seeders, num_leechers, comment, dispersy_id, CAST(torrent_file_name AS INTEGER),
last_tracker_check, tracker_check_retries, next_tracker_check FROM Torrent;

DROP TABLE Torrent;
ALTER TABLE _tmp_Torrent RENAME TO Torrent;

DROP VIEW IF EXISTS CollectedTorrent;
CREATE VIEW CollectedTorrent AS SELECT * FROM Torrent WHERE is_collected == 1;
""")

        # update database version
        self.db.write_version(26)