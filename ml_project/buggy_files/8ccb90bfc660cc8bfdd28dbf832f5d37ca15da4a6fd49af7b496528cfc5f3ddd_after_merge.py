    def to_pack_list(self):
        data = [('20s', str(self.infohash)),
                ('varlenH', self.name.encode('utf-8')),
                ('Q', self.length),
                ('I', self.num_files),
                ('varlenH', encode_values(self.category_list)),
                ('l', self.creation_date),
                ('I', self.seeders),
                ('I', self.leechers),
                ('20s', self.cid if self.cid else '')]
        return data