    def __delitem__(self, key):
        self._detyped = None
        old_value = self._d.get(key, None)
        del self._d[key]
        events.on_lscolors_change.fire(key=key, oldvalue=old_value, newvalue=None)