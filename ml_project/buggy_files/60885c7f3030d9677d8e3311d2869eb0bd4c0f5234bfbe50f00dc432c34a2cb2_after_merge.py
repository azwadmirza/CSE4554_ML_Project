    def to_pack_list(self):
        data = [('20s', self.infohash),
                ('varlenH', self.name.encode('utf-8')),
                ('I', self.length),
                ('I', self.creation_date),
                ('I', self.num_files),
                ('varlenH', str(self.comment))]
        return data