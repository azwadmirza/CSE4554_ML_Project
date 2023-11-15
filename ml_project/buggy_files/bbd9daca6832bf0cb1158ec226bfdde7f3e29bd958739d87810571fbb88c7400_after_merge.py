    def __del__(self):
        # Explicitly load the content from shared memory to delete it
        # Unfortunately it seems the way the data is pickled prevents efficient implicit GarbageCollection
        try:
            for k in list(self._data_buffer.keys()):
                res = pickle.loads(self._data_buffer.pop(k).get(self._timeout))
                del res
        except FileNotFoundError:
            # The resources were already released
            pass