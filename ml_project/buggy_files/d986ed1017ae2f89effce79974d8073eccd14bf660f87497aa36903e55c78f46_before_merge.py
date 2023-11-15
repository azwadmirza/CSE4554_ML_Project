    def _store_object(self, obj):
        self._wr = weakref.ref(obj)