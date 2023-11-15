    def set(self, key, value, state):
        key = bytes_to_str(key)
        data = {'_id': key, 'value': value}
        try:
            self.connection.save(data)
        except pycouchdb.exceptions.Conflict:
            # document already exists, update it
            data = self.connection.get(key)
            data['value'] = value
            self.connection.save(data)