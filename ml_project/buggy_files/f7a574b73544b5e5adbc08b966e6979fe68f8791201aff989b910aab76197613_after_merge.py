    def save_many(self, sitename, data):
        # Work-around for https://github.com/internetarchive/openlibrary/issues/4285
        # Infogami seems to read encoded bytes as a string with a byte literal inside
        # of it, which is invalid JSON and also can't be decode()'d.
        if isinstance(data.get('query'), bytes):
            data['query'] = data['query'].decode()
        return self.conn.request(sitename, '/save_many', 'POST', data)