    def _upgrade_18_to_22(self):
        self.current_status = u"Upgrading database from v%s to v%s..." % (18, 22)

        self.db.execute(u"""
DROP INDEX IF EXISTS Torrent_swift_hash_idx;

DROP VIEW IF EXISTS Friend;

ALTER TABLE Peer RENAME TO __Peer_tmp;
CREATE TABLE IF NOT EXISTS Peer (
    peer_id    integer PRIMARY KEY AUTOINCREMENT NOT NULL,
    permid     text NOT NULL,
    name       text,
    thumbnail  text
);

INSERT INTO Peer (peer_id, permid, name, thumbnail) SELECT peer_id, permid, name, thumbnail FROM __Peer_tmp;

DROP TABLE IF EXISTS __Peer_tmp;

ALTER TABLE Torrent ADD COLUMN last_tracker_check integer DEFAULT 0;
ALTER TABLE Torrent ADD COLUMN tracker_check_retries integer DEFAULT 0;
ALTER TABLE Torrent ADD COLUMN next_tracker_check integer DEFAULT 0;

CREATE TABLE IF NOT EXISTS TrackerInfo (
  tracker_id  integer PRIMARY KEY AUTOINCREMENT,
  tracker     text    UNIQUE NOT NULL,
  last_check  numeric DEFAULT 0,
  failures    integer DEFAULT 0,
  is_alive    integer DEFAULT 1
);

CREATE TABLE IF NOT EXISTS TorrentTrackerMapping (
  torrent_id  integer NOT NULL,
  tracker_id  integer NOT NULL,
  FOREIGN KEY (torrent_id) REFERENCES Torrent(torrent_id),
  FOREIGN KEY (tracker_id) REFERENCES TrackerInfo(tracker_id),
  PRIMARY KEY (torrent_id, tracker_id)
);

INSERT OR IGNORE INTO TrackerInfo (tracker) VALUES ('no-DHT');
INSERT OR IGNORE INTO TrackerInfo (tracker) VALUES ('DHT');

DROP INDEX IF EXISTS torrent_biterm_phrase_idx;
DROP TABLE IF EXISTS TorrentBiTermPhrase;
DROP INDEX IF EXISTS termfrequency_freq_idx;
DROP TABLE IF EXISTS TermFrequency;
DROP INDEX IF EXISTS Torrent_insert_idx;
DROP INDEX IF EXISTS Torrent_info_roothash_idx;

DROP TABLE IF EXISTS ClicklogSearch;
DROP INDEX IF EXISTS idx_search_term;
DROP INDEX IF EXISTS idx_search_torrent;
""")
        # update database version
        self.db.write_version(22)