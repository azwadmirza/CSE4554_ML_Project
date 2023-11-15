    def save_many(self, sitename, data):
        return self.conn.request(sitename, '/save_many', 'POST', data)