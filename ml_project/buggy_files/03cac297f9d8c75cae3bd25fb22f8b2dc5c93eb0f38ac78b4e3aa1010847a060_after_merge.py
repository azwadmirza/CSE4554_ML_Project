    def _upgrade_26_to_27(self):
        self.status_update_func(u"Upgrading database from v%s to v%s..." % (26, 27))

        # replace status_id and category_id in Torrent table with status and category
        self.status_update_func(u"Updating Torrent table and removing unused tables...")
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
  category         text,
  status           text DEFAULT 'unknown',
  num_seeders      integer,
  num_leechers     integer,
  comment          text,
  dispersy_id      integer,
  is_collected     integer DEFAULT 0,
  last_tracker_check    integer DEFAULT 0,
  tracker_check_retries integer DEFAULT 0,
  next_tracker_check    integer DEFAULT 0
);

INSERT INTO _tmp_Torrent
SELECT torrent_id, infohash, T.name, length, creation_date, num_files, insert_time, secret, relevance, C.name, TS.name,
num_seeders, num_leechers, comment, dispersy_id, is_collected, last_tracker_check, tracker_check_retries,
next_tracker_check
FROM Torrent AS T
LEFT JOIN Category AS C ON T.category_id == C.category_id
LEFT JOIN TorrentStatus AS TS ON T.status_id == TS.status_id;

DROP VIEW IF EXISTS CollectedTorrent;
DROP TABLE Torrent;
ALTER TABLE _tmp_Torrent RENAME TO Torrent;
CREATE VIEW CollectedTorrent AS SELECT * FROM Torrent WHERE is_collected == 1;

DROP TABLE Category;
DROP TABLE TorrentStatus;
""")

        # update database version
        self.db.write_version(27)