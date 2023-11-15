    def write_initial(self, msg, obj_index):
        if msg is None:
            return
        return self._write_noansi(msg, obj_index, '')