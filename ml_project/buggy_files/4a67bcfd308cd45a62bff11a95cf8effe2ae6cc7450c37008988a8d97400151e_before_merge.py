    def _dump_to_file(self, open_file):
        cache_obj_dump = json.dumps({
            '_last_touched': self._last_touched,
            '_payload': self._payload
        })
        open_file.write(cache_obj_dump)