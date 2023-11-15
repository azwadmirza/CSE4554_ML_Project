    def update_torrent_with_metainfo(self, infohash, metainfo):
        """ Updates name, length and num files from metainfo if record does not exist in the database. """
        torrent_id = self.getTorrentID(infohash)
        name = self.getOne('name', torrent_id=torrent_id)
        if not name:
            num_files, length = 0, 0
            if 'info' in metainfo:
                info = metainfo['info']
                name = u''.join([unichr(ord(c)) for c in info["name"]]) if "name" in info else ""
                if 'files' in info:
                    num_files = len(info['files'])
                    for piece in info['files']:
                        length += piece['length']

            if name and num_files and length:
                self.updateTorrent(infohash, notify=False, name=name, num_files=num_files, length=length)