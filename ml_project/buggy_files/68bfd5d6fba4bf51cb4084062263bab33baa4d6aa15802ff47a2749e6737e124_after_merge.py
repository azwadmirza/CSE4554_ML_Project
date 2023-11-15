    def _set_keys(self, keys):
        if keys is not None:
            if isinstance(keys, string_types):
                if keys != 'interactive':
                    raise ValueError('keys, if string, must be "interactive", '
                                     'not %s' % (keys,))

                def toggle_fs():
                    self.fullscreen = not self.fullscreen
                keys = dict(escape='close', F11=toggle_fs)
        else:
            keys = {}
        if not isinstance(keys, dict):
            raise TypeError('keys must be a dict, str, or None')
        if len(keys) > 0:
            # ensure all are callable
            for key, val in keys.items():
                if isinstance(val, string_types):
                    new_val = getattr(self, val, None)
                    if new_val is None:
                        raise ValueError('value %s is not an attribute of '
                                         'Canvas' % val)
                    val = new_val
                if not hasattr(val, '__call__'):
                    raise TypeError('Entry for key %s is not callable' % key)
                # convert to lower-case representation
                keys.pop(key)
                keys[key.lower()] = val
            self._keys_check = keys

            def keys_check(event):
                if event.key is not None:
                    use_name = event.key.name.lower()
                    if use_name in self._keys_check:
                        self._keys_check[use_name]()
            self.events.key_press.connect(keys_check, ref=True)