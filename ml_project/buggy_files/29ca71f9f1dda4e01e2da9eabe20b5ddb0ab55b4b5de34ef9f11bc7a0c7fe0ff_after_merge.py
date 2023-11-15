    def __setitem__(self, key, value):
        self._detyped = None
        old_value = self._d.get(key, None)
        self._targets.discard(key)
        if value == LsColors.target_value:
            value = LsColors.target_color
            self._targets.add(key)
        self._d[key] = value
        if (
            old_value != value
        ):  # bug won't fire if new value is 'target' and old value happened to be no color.
            events.on_lscolors_change.fire(key=key, oldvalue=old_value, newvalue=value)