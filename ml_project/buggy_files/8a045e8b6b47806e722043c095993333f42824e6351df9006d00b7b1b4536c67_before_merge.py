    def __setitem__(self, key, value):
        log.debug('setting key %s value %s' % (key, repr(value)))
        self.store[key] = value