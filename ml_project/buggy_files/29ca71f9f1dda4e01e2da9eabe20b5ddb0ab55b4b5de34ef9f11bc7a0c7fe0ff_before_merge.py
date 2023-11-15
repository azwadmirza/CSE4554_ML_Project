    def __setitem__(self, key, value):
        self._detyped = None
        old_value = self._d.get(key, None)
        self._d[key] = value
        if old_value != value:
            events.on_lscolors_change.fire(key=key, oldvalue=old_value, newvalue=value)