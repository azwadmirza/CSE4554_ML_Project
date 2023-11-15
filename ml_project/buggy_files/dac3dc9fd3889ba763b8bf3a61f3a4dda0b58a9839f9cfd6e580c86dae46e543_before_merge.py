    def get_old_channels(self):
        connection = sqlite3.connect(self.tribler_db)
        cursor = connection.cursor()

        channels = []
        for id_, name, dispersy_cid, modified, nr_torrents, nr_favorite, nr_spam in cursor.execute(
                self.select_channels_sql):
            if nr_torrents and nr_torrents > 0:
                channels.append({"id_": infohash_to_id(dispersy_cid),
                                 # converting this to str is a workaround for python 2.7 'writable buffers not hashable'
                                 # problem with Pony
                                 "infohash": str(dispersy_cid),
                                 "title": name or '',
                                 "public_key": NULL_KEY,
                                 "timestamp": final_timestamp(),
                                 "origin_id": 0,
                                 "size": 0,
                                 "subscribed": False,
                                 "status": LEGACY_ENTRY,
                                 "num_entries": int(nr_torrents or 0)})
        connection.close()
        return channels