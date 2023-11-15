    def delete_password(self, servicename, username):
        self.keys[servicename][username] = None