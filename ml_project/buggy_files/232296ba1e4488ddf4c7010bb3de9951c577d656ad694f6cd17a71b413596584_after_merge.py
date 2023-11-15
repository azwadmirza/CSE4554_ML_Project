    def pack_identifier(self):
        """Return a combined identifier for the whole pack if this has more than one episode."""
        # Currently only supports ep mode
        if self.id_type == 'ep':
            if self.episodes > 1:
                return 'S%02dE%02d-E%02d' % (self.season, self.episode, self.episode + self.episodes - 1)
            else:
                return self.identifier
        else:
            return self.identifier