    def _dump_to_file(self, open_file):
        cache_obj_dump = json.dumps({
            'last_saved': self.last_saved,
            '_payload': self._payload
        })
        open_file.write(cache_obj_dump)