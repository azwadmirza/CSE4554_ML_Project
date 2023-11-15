    def load(self, key):
        for base in self._read_dirs:
            path = os.path.join(base, key)
            if not os.path.isfile(path):
                continue
            try:
                with open(path, mode='r') as f:
                    data = f.read().strip()
                    if len(data) == 0:
                        value = None
                    else:
                        value = literal_eval(data)
                    _LOGGER.debug('loaded %s=%r (from %s)', key, value, path)
            except OSError as err:
                _LOGGER.warning('%s exists but could not be read: %s', path, err)
            except ValueError as err:
                _LOGGER.warning('%s exists but was corrupted: %s', key, err)
            else:
                return value

        _LOGGER.debug('no data (file) found for %s', key)
        return None