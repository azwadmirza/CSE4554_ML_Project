        def get_updated_channels(cls):
            return select(g for g in cls if g.subscribed and (g.local_version < g.timestamp))