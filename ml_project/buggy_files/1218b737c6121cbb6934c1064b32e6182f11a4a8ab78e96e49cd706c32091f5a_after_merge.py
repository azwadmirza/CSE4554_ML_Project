    def from_unpack_list(cls, dbid, dispersy_cid, name, description, nr_torrents, nr_favorite, nr_spam, modified):
        return ChannelItemPayload(dbid, dispersy_cid, name.decode('utf-8'), description.decode('utf-8'), nr_torrents,
                                  nr_favorite, nr_spam, modified)