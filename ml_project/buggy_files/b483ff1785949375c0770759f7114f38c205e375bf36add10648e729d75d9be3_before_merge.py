    def to_pack_list(self):
        data = [('I', id),
                ('20s', str(self.cid)),
                ('varlenH', self.name),
                ('varlenH', self.description),
                ('I', self.nr_torrents),
                ('I', self.nr_favorite),
                ('I', self.nr_spam),
                ('I', self.modified)]
        return data