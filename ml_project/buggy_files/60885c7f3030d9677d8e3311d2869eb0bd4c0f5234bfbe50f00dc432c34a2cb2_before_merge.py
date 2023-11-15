    def to_pack_list(self):
        data = [('20s', self.infohash),
                ('varlenH', str(self._name)),
                ('I', self._length),
                ('I', self._creation_date),
                ('I', self._num_files),
                ('varlenH', str(self._comment))]
        return data