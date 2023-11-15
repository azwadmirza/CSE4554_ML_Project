    def __setitem__(self, key, value):
        # Enforce unicode compatibility.
        if PY2 and isinstance(value, native_str):
            # Allow Python 2's implicit string decoding, but fail now instead of when entry fields are used.
            # If encoding is anything but ascii, it should be decoded it to text before setting an entry field
            try:
                value = value.decode('ascii')
            except UnicodeDecodeError:
                raise EntryUnicodeError(key, value)
        elif isinstance(value, bytes):
            raise EntryUnicodeError(key, value)

        # url and original_url handling
        if key == 'url':
            if not isinstance(value, (str, LazyLookup)):
                raise PluginError('Tried to set %r url to %r' % (self.get('title'), value))
            self.setdefault('original_url', value)

        # title handling
        if key == 'title':
            if not isinstance(value, (str, LazyLookup)):
                raise PluginError('Tried to set title to %r' % value)

        try:
            log.trace('ENTRY SET: %s = %r' % (key, value))
        except Exception as e:
            log.debug('trying to debug key `%s` value threw exception: %s' % (key, e))

        super(Entry, self).__setitem__(key, value)