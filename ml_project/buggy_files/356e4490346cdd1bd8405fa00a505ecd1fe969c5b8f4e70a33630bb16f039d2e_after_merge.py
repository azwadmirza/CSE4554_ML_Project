        def get_updated_channels(cls):
            return select(g for g in cls if g.subscribed and
                          g.status != LEGACY_ENTRY and
                          (g.local_version < g.timestamp) and
                          g.public_key != database_blob(cls._my_key.pub().key_to_bin()[10:]))